from shiny import App, reactive, render, ui, module
from eval_prompt import set_prompt, evaluate_prompt
import json
import asyncio

@module.ui
def attr_exp_assisted_mode_ui():
    return ui.card(ui.div(
                        ui.output_ui("render_starting_ui_assisted_mode"),
                        ui.output_ui("render_current_implication_output_assisted_mode"),
                     ),
                     ui.div(
                        ui.output_ui("model_response_output_assisted_mode"),
                     ),
                    ui.div(
                        ui.output_ui("model_response_button_assisted_mode"),
                        ui.output_ui("model_response_action_button_assisted_mode"),
                        ui.output_ui("render_manual_input_controls"),
                        ui.output_ui("render_implication_message_ui"),
                     ),
                )


@module.server
def attr_exp_assisted_mode_server(input, output, session, cxt, trigger_recalc, selected_attr_index):

    toggle_state_assisted_mode = reactive.Value(True)
    implication_message_assisted_mode = reactive.value(None)

    manual_input_toggle_assisted_mode = reactive.value(False)
    models_response_state = reactive.value(None)
    prompt_body_state = reactive.value([])

    @output
    @render.ui
    def render_starting_ui_assisted_mode():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file. from module", style="color: red; margin-top: 100px; margin-left: 30px;"),
                style="margin-top: 30px; margin-left: 24px;"
            )
        else:
            return ui.div("")

    @output
    @render.ui
    def render_current_implication_output_assisted_mode():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_current_implications(selected_attr_index.get())
            return ui.div(
                ui.strong(f"Current Implication : {implication}"),
                style="text-align: center; margin-top: 45px; margin-bottom: 30px;",
            )
        return ui.div("")

    @output
    @render.ui
    def model_response_button_assisted_mode():
        context = cxt.get()
        if context is not None:
            return ui.div(
                ui.input_action_button("get_model_response", "Ask the Model", class_="btn btn-outline-primary",
                                       style="margin-top: 20px;", ),
                ui.p("^ Please wait while the response is being generated. Press the button only once.",
                     style="font-size: 12px; margin-top: 10px; margin-bottom: 0px;"),
                ui.p("# If the response is unsatisfactory, you may press the button again to regenerate it.",
                     style="font-size: 12px; margin-top: 0px; margin-bottom: 0px;"),

                style="display: flex; flex-direction: column; align-items: center;"
            )
        else:
            return ui.div("")

    @output
    @render.ui
    def model_response_output_assisted_mode():
        result = models_response_state.get()
        if result is not None:
            if result['output'] == "YES":
                return ui.card(
                    ui.h6(f"Agents's Response:"),
                    ui.div(f"The agent say's the implication is valid"),
                )
            elif result['output'] == "NO":
                return ui.div(
                    ui.h6("Agent's Response:", style="font-weight: bold; margin-bottom: 4px;"),
                    ui.HTML(
                        "<div style='margin-bottom: 0px;'>The agent indicates that the implication is invalid.</div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px;'>Suggested counterexample word: <strong>{result['word']}</strong></div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px;'>Meaning(s) associated with this word: <strong>{', '.join(result['meaning'])}</strong></div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px; margin-top:20px'><em>Explanation given by the Agent: {result['explanation']}</em></div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px; margin-top:20px'><em>Example given by the Agent: {result['example']}</em></div>"),
                    style="text-align: center;"
                )
            else:
                return ui.div(
                    ui.h6("Agent's provided a invalid response, Please try again", style="font-weight: bold; margin-bottom: 4px;"),
                )
        else:
            return ui.div("")

    @output
    @render.ui
    def model_response_action_button_assisted_mode():
        context = cxt.get()
        if context is not None and models_response_state.get() is not None:
            return ui.div(
                ui.layout_columns(
                    ui.h3(""),
                    ui.div(
                        ui.input_action_button("confirm_model_response", "Confirm Model Response", class_="btn-success",
                                               style="margin-top: 20px;", ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.div(
                        ui.input_action_button("reject_model_response", "Manual Input", class_="btn-warning",
                                               style="margin-top: 20px;", ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.h3(""),
                    col_widths=(1, 5, 5, 1),
                )
            )
        else:
            return ui.div("")



    @reactive.effect
    @reactive.event(input.get_model_response)
    def handle_model_response_generation():
        trigger_recalc.set(trigger_recalc.get() + 1)
        context = cxt.get()
        manual_input_toggle_assisted_mode.set(False)
        if context is not None:

            attributes = context.Basic_Exploration.context.attributes
            objects = context.Basic_Exploration.context.objects
            examples = context.Basic_Exploration.examples

            premise, conclusion = context.Basic_Exploration.get_implication_premise_conclusion_for_prompt(
                selected_attr_index.get())

            df = context.Basic_Exploration.get_context_dataframe()

            prompt = set_prompt(
                objects=objects,
                frames=attributes,
                examples=examples,
                premise=premise,
                conclusion=conclusion,
                df=df
            )

            set_prompts = prompt_body_state.get()
            set_prompts.append({"role": "user", "content": prompt})
            result_str = evaluate_prompt(set_prompts)

            try :
                result = json.loads(result_str)

            except json.decoder.JSONDecodeError as e:
                result = json.dumps({"output": "INVALID"})



            set_prompts.append({"role": "assistant", "content": result_str})
            prompt_body_state.set(set_prompts)

            models_response_state.set(result)

            current_implication = context.Basic_Exploration.get_current_implications(selected_attr_index.get())
            implication_message_assisted_mode.set(
                ui.accordion(
                    ui.accordion_panel("Chat with the agent",
                                       ui.card(
                                           ui.card_header("FCA ChatBot"),
                                           ui.chat_ui("chat", messages=["You can chat with the agent here"],
                                                      width="100%"),
                                           style="width:min(680px, 100%)",
                                           class_="mx-auto",
                                       ),
                                       ),
                    ui.accordion_panel("Inspect Prompt sent to the agent",
                                       ui.HTML(f"<pre>"
                                               f"Implication being tested:\n"
                                               f"{current_implication}\n\n\n"
                                               f"Prompt sent to the agent for this implication:\n\n"
                                               f"{prompt}"
                                               f"</pre>"),
                                       ),
                    id="acc",
                    open=False,
                ),
            )
        else:
            models_response_state.set(None)

    chat = ui.Chat(id="chat")

    @chat.on_user_submit
    async def handle_user_chat_input(user_input: str):
        model_input = user_input.strip()
        context = cxt.get()
        if context is not None:

            set_prompts = prompt_body_state.get()
            add_on_prompt = ""
            if "format" not in model_input:
                add_on_prompt = " and don't respond with a json object"

            set_prompts.append({"role": "user", "content": f"{model_input},{add_on_prompt}"})
            result_str = evaluate_prompt(set_prompts)

            if "output" in result_str:
                try:
                    response_json = json.loads(result_str)
                    models_response_state.set(response_json)
                except Exception as e:
                    print(e)

            set_prompts.append({"role": "assistant", "content": result_str})
            prompt_body_state.set(set_prompts)
            await chat.append_message(result_str)

    # when the user wants manual input instead of confirming the model response
    @reactive.effect
    @reactive.event(input.reject_model_response)
    def handle_manual_input_controls():
        manual_input_toggle_assisted_mode.set(True)
        implication_message_assisted_mode.set("")

    @reactive.effect
    @reactive.event(input.confirm_model_response)
    def handle_confirm_model_response():
        manual_input_toggle_assisted_mode.set(False)
        toggle_state_assisted_mode.set(True)

        model_response = models_response_state.get()
        if model_response is not None:
            if model_response['output'] == "NO":
                context = cxt.get()
                counter_example_word = model_response["word"]
                counter_example_meanings = model_response["meaning"]
                out = context.Basic_Exploration.set_counter_example(counter_example_word, counter_example_meanings,
                                                                selected_attr_index.get())
                if out[0] == "PASS":
                    trigger_recalc.set(trigger_recalc.get() + 1)
                    out_log = "Previous Model Response Confirmed, Counter Examples added."
                    msg = ui.h6(f'{a}', style="color: Blue; text-align: center; font-weight: bold;")
                    implication_message_assisted_mode.set(msg)

                if out[0] == "FAIL":
                    out_log = "Previous Model Response is invalid, Please generate model response again."
                    msg = ui.div(
                        ui.h6(f'{out_log}', style="color: Red; text-align: center; font-weight: bold;"),
                        ui.h6(f'{out[1]}', style="color: Red; text-align: center; font-weight: bold;")
                    )
                    implication_message_assisted_mode.set(msg)

                models_response_state.set(None)
            elif model_response['output'] == "YES":
                trigger_recalc.set(trigger_recalc.get() + 1)
                context = cxt.get()
                context.Basic_Exploration.post_confirm_implications(selected_attr_index.get())
                msg = ui.h6(f'Previous Model Response Confirmed, Implication confirmed.', style="color: Blue; text-align: center; font-weight: bold;")
                implication_message_assisted_mode.set(msg)
                models_response_state.set(None)
            else:
                msg = ui.h6(f'Previous Model Response is invalid, Please generate model response again.',
                            style="color: Red; text-align: center; font-weight: bold;")
                implication_message_assisted_mode.set(msg)

        else:
            implication_message_assisted_mode.set("")

    @output
    @render.ui
    def render_manual_input_controls():
        if manual_input_toggle_assisted_mode():
            if toggle_state_assisted_mode():
                reject = ui.input_action_button(
                    "toggle_button_assisted_mode", "reject implication",
                    class_="btn btn-outline-warning", style="margin-top: 20px; width: 250px;",
                )
            else:
                reject = ui.input_action_button(
                    "toggle_button_assisted_mode", "confirm counter example",
                    class_="btn btn-outline-primary", style="margin-top: 20px; width: 250px;")

            msg = ui.div(
                ui.h6("Provide Manual Input:", style="text-align:center;font-weight: bold; margin-bottom: 4px;"),
                ui.layout_columns(
                    ui.h3(""),
                    ui.input_action_button("confirm_implication_assisted_mode", "confirm implication",
                                           class_="btn btn-outline-success",
                                           style="margin-top: 20px;width: 250px;", ),
                    reject,
                    ui.h3(""),
                    col_widths=(1, 5, 5, 1),
                ))
            return msg
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.toggle_button_assisted_mode)
    def handle_toggle_action_assisted_mode():
        if toggle_state_assisted_mode():
            context = cxt.get()
            trigger_recalc.set(trigger_recalc.get() + 1)
            attributes = context.Basic_Exploration.attributes

            out = ui.div(
                ui.h6(f'Implication Rejected',
                      style="color: Red; text-align: center; font-weight: bold; margin-top: 20px;"),
                ui.h6(f'Provide Counter Example below',
                      style="color: Black; text-align: center; margin-top: 20px; margin-bottom: 20px;"),
                ui.layout_columns(
                    ui.div(
                        ui.h6("Enter Counter Object", style="margin-bottom: 20px;"),
                        ui.input_text("counter_object_text_assisted_mode", "", "object"),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.div(
                        ui.h6("Enter Counter Object's Attributes", style="margin-bottom: 20px;"),
                        ui.input_checkbox_group(  # <<
                            "counter_attribute_checkbox_assisted_mode",  # <<
                            "",
                            attributes,
                        ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                ),
            )
            implication_message_assisted_mode.set(out)

        else:
            try:
                context = cxt.get()
                counter_object = input.counter_object_text_assisted_mode()
                counter_attributes = input.counter_attribute_checkbox_assisted_mode()

                if counter_object in objects:
                    b = ui.div(
                        ui.h6(f'Counter Example is Invalid',
                              style="color: Red; text-align: center; font-weight: bold;"),
                        ui.h6(f'Object with the name "{counter_object}" already present in the context.',
                              style="color: Red; text-align: center; font-weight: bold;")
                    )
                    print_implications.set(b)

                else:
                    out = context.Basic_Exploration.set_counter_example(counter_object, counter_attributes,
                                                                    selected_attr_index.get())
                    if out[0] == "PASS":
                        trigger_recalc.set(trigger_recalc.get() + 1)
                        a = "Previous Counter Example has been Confirmed."
                        b = ui.h6(f'{a}', style="color: Blue; text-align: center; font-weight: bold;")
                        implication_message_assisted_mode.set(b)

                    if out[0] == "FAIL":
                        a = "Counter Example is invalid."
                        b = ui.div(
                            ui.h6(f'{a}', style="color: Red; text-align: center; font-weight: bold;"),
                            ui.h6(f'{out[1]}', style="color: Red; text-align: center; font-weight: bold;")
                        )
                        implication_message_assisted_mode.set(b)

            except Exception as e:
                pass
        toggle_state_assisted_mode.set(not toggle_state_assisted_mode())

    @reactive.effect
    @reactive.event(input.confirm_implication_assisted_mode)
    def handle_manual_implication_confirmation():
        if input.confirm_implication_assisted_mode():
            trigger_recalc.set(trigger_recalc.get() + 1)
            context = cxt.get()
            if context is not None:
                toggle_state_assisted_mode.set(True)
                context.Basic_Exploration.post_confirm_implications(selected_attr_index.get())
                a = "Previous Implication Confirmed."
                b = ui.h6(f'{a}', style="color: Green; text-align: center; font-weight: bold;")
                implication_message_assisted_mode.set(b)
        else:
            implication_message_assisted_mode.set("")

    @output
    @render.ui
    def render_implication_message_ui():
        msg = implication_message_assisted_mode.get()
        if msg is not None:
            return ui.div(msg)
        else:
            return ui.div("")