from shiny import App, reactive, render, ui, module
from eval_prompt import set_prompt, evaluate_prompt
import json
import random
from datetime import date, datetime
import re


@module.ui
def attr_exp_auto_mode_ui():
    return ui.card(ui.div(
        ui.output_ui("render_starting_ui_auto_mode"),
    ),
        ui.div(
            ui.output_ui("render_steps_and_prompt_input_button"),
            ui.output_ui("render_start_exploration_button_auto_mode"),
            ui.output_ui("render_exploration_log_auto_mode"),
        ),
    )


@module.server
def attr_exp_auto_mode_server(input, output, session, cxt, trigger_recalc):
    trigger_response = reactive.value(None)
    prompt_body_state_auto = reactive.value([{"role": "System",
                                              "content": "Restrict your responses to English words"}])
    steps_state = reactive.value(100)


    implication_generator = reactive.value(None)
    word_already_present_error_count = reactive.value(0)
    json_format_error_count = reactive.value(0)
    invalid_counter_example_error_count = reactive.value(0)
    implication_count = reactive.value(0)
    confirmed_implications = reactive.value(0)
    skipped_implications = reactive.value(0)
    rejected_implications = reactive.value(0)
    logs_attr = reactive.value([])

    @output
    @render.ui
    def render_starting_ui_auto_mode():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file.",
                          style="color: red; margin-top: 100px; margin-left: 30px;"),
                style="margin-top: 30px; margin-left: 24px;"
            )
        else:
            return ui.div("")

    @reactive.effect
    def start_implication_generator():
        context = cxt.get()
        if context is not None:
            implication_generator.set(context.Basic_Exploration.relative_basis_generator_for_auto_mode())
        return None

    @output
    @render.ui
    def render_steps_and_prompt_input_button():
        context = cxt.get()
        if context is not None:
            return ui.layout_columns(
                ui.input_text_area("system_prompt", "System Prompt",
                                   "Restrict your responses to English words"),
                ui.input_numeric("steps", "Implications to process before stopping", 100, min=1, max=3000),
            )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.system_prompt)
    def handle_system_prompt_input():
        if input.system_prompt() is not None:
            prompt = [{"role": "System", "content": input.system_prompt()}]
            prompt_body_state_auto.set(prompt)

    @reactive.effect
    @reactive.event(input.steps)
    def handle_number_of_steps_input():
        if steps_state.get() is not None:
            steps_state.set(input.steps())

    @output
    @render.ui
    def render_start_exploration_button_auto_mode():
        context = cxt.get()
        if context is not None:
            return ui.div(
                ui.input_action_button("start_exploration", "Start Exploration", class_="btn-success",
                                       style="margin-top: 10px;width: 250px;", ),
                ui.strong("❗️❗❗️This process starts from the first implication by default",
                          style="font-size: 12px;color:red; margin-top: 10px;"),
                ui.p("^ Please press the button only once",
                     style="font-size: 12px; margin-top: 10px; margin-bottom: 0px;"),
                ui.p("^ The process will only end once the exploration is complete",
                     style="font-size: 12px;margin-bottom: 0px;"),
                style="display: flex; flex-direction: column; align-items: center; margin-top: 50px;",
            )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.start_exploration)
    def handle_start_exploration_button_auto_mode():
        if input.start_exploration():
            trigger_response.set("Start")

    def get_model_response(premise, conclusion, context):
        n = 3  # number of tries
        print("\n-----------------------------")

        result_list = list()

        if context is not None:
            for i in range(n):
                results = {"try": i + 1}
                imp = " , ".join(premise) + " => " + " , ".join(conclusion)
                print("Try : ", i + 1, " For : ", imp)

                examples = context.Basic_Exploration.examples
                attributes = context.Basic_Exploration.context.attributes
                objects = context.Basic_Exploration.context.objects
                print("Current Objects : ", objects)

                df = context.Basic_Exploration.get_context_dataframe()

                prompt = set_prompt(
                    objects=objects,
                    frames=attributes,
                    examples=examples,
                    premise=premise,
                    conclusion=conclusion,
                    df=df
                )

                set_prompts = prompt_body_state_auto.get()

                if set_prompts[-1]["role"] != "user":
                    set_prompts.append({"role": "user", "content": prompt})

                result_str = evaluate_prompt(set_prompts)
                set_prompts.append({"role": "assistant", "content": result_str})

                try:
                    result = json.loads(result_str)
                    results["model_response"] = result
                    result["word"] = re.sub(r"\s*:\s*", ":", result["word"])

                except json.decoder.JSONDecodeError:
                    json_format_error_count.set(json_format_error_count.get() + 1)
                    results["model_response"] = result_str
                    results["attempt_outcome"] = f"Json decoder error"
                    result_list.append(results)
                    print("Json decoder error")
                    set_prompts.append(
                        {"role": "user",
                         "content": f"Please respond again with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."})
                    prompt_body_state_auto.set(set_prompts)
                    continue

                if result["output"] == "NO" and result["word"] in objects:
                    word_already_present_error_count.set(word_already_present_error_count.get() + 1)
                    results["attempt_outcome"] = f"Attribute already present error"
                    result_list.append(results)
                    print(result["word"]," : word already present error")
                    set_prompts.append(
                        {"role": "user",
                         "content": f"word '{result["word"]}' already present in the context, please use another counterexample, or confirm the hypothesis."})
                    prompt_body_state_auto.set(set_prompts)
                    continue

                if result["output"] == "NO":
                    try:
                        print("Implication rejected, with CE word : ", result['word'], "with associated meanings : ",
                              result['meaning'])
                        context.Basic_Exploration.check_counter_example_for_attr_auto_mode(result["meaning"], premise,
                                                                                           conclusion,
                                                                                           context.Basic_Exploration.confirmed_attribute_implications)

                        results["attempt_outcome"] = f"Valid Counter Example"
                        result_list.append(results)
                        print("Counter Example is Valid, setting the result")
                        trigger_recalc.set(trigger_recalc.get() + 1)
                        prompt_body_state_auto.set([{"role": "System", "content": input.system_prompt()}])
                        return result, result_list

                    except Exception as e:
                        invalid_counter_example_error_count.set(invalid_counter_example_error_count.get() + 1)
                        print("Invalid Counter example : ", e)
                        results["attempt_outcome"] = f"Invalid Counter example"
                        result_list.append(results)
                        set_prompts.append(
                            {"role": "user",
                             "content": f"The counter example that you provided is invalid because {e}"})
                        prompt_body_state_auto.set(set_prompts)
                        pass

                elif result["output"] == "YES":
                    print("Implication Accepted, setting the result")
                    results["attempt_outcome"] = f"Implication Accepted"
                    result_list.append(results)
                    trigger_recalc.set(trigger_recalc.get() + 1)
                    prompt_body_state_auto.set([{"role": "System", "content": input.system_prompt()}])
                    return result, result_list

            print(f"Maximum tries reached, implication is skipped")
            response_content = json.dumps({"output": "SKIP"})
            result = json.loads(response_content)
            return result, result_list

        else:
            return None

    def set_result(result, context):
        if result["output"] == "NO":
            context.Basic_Exploration.set_counter_example_auto(result["word"], result["meaning"])
            trigger_recalc.set(trigger_recalc.get() + 1)
            return "Rejected", set(result["meaning"])

        elif result["output"] == "YES":
            trigger_recalc.set(trigger_recalc.get() + 1)
            return "Confirmed", ""

        elif result["output"] == "SKIP":
            trigger_recalc.set(trigger_recalc.get() + 1)
            return "Skipped", ""
        else:
            return None

    @reactive.effect
    def run_exploration():
        if trigger_response.get() == "Start":
            trigger_response.set("stop")
            i = 0

            generator = implication_generator.get()
            context = cxt.get()

            for imp in generator:
                i += 1
                log_entry = {"imp id": i,
                             "full_implication": f"{' , '.join(list(imp._premise))} -> {' , '.join(list(imp.get_reduced_conclusion()))}"}

                while imp._premise != imp._conclusion:
                    if len(imp._premise) == 0:
                        log_entry["result"] = "Confirmed"
                        logs_list.append(log_entry)
                        implication_count.set(implication_count.get() + 1)
                        confirmed_implications.set(confirmed_implications.get() + 1)
                        context.Basic_Exploration.confirm_attribute_implication_auto_mode(imp)
                        break

                    implication_count.set(implication_count.get() + 1)
                    model_response, model_response_log = get_model_response(imp.premise, imp.get_reduced_conclusion(), context)
                    log_entry["exploration_output"] = model_response_log
                    result, counter_intent = set_result(model_response, context)

                    if result == "Rejected":
                        log_entry["result"] = "Implication Rejected"
                        rejected_implications.set(rejected_implications.get() + 1)
                        imp._conclusion &= counter_intent
                        break

                    elif result == "Skipped":
                        log_entry["result"] = "Implication Skipped"
                        skipped_implications.set(skipped_implications.get() + 1)
                        break
                    else:
                        log_entry["result"] = "Implication Confirmed"
                        confirmed_implications.set(confirmed_implications.get() + 1)
                        context.Basic_Exploration.confirm_attribute_implication_auto_mode(imp)
                        break

                logs = logs_attr.get()
                logs.append(log_entry)
                logs_attr.set(logs)

                if i == int(steps_state.get()):
                    print("\nObject check limit reached")

            analysis_log_entry = {"imp id": 999999,
                                  "output_objects": context.Basic_Exploration.context.objects,
                                  "output_attributes": context.Basic_Exploration.context.attributes,
                                  "implication_count": implication_count.get(),
                                  "implications_skipped": skipped_implications.get(),
                                  "implications_confirmed": confirmed_implications.get(),
                                  "implications_rejected": rejected_implications.get(),
                                  "invalid_counter_examples": invalid_counter_example_error_count.get(),
                                  "json_format_error": json_format_error_count.get(),
                                  "word_already_present_error": word_already_present_error_count.get()}

            logs = logs_attr.get()
            logs.append(analysis_log_entry)
            logs_attr.set(logs)


            print("Invalid Counter examples : ", invalid_counter_example_error_count.get())
            print("Json Format Error : ", json_format_error_count.get())
            print("word Already Present error : ", word_already_present_error_count.get())
            print("Implication Count: ", implication_count.get())
            print("Implications skipped: ", skipped_implications.get())
            print("Implications Confirmed: ", confirmed_implications.get())
            print("----------Exploration Ended----------")


    @output
    @render.ui
    def render_exploration_log_auto_mode():
        return ui.div(
            ui.download_button("download_log_obj", "Download Log", class_="btn btn-outline-primary",
                               style="text-align: center; font-size: 12px; width: 190px;"),
            style="display: flex; flex-direction: column; align-items: center; margin-top: 50px;")

    @output
    @render.download(filename=lambda: f"attribute_exp_log_{date.today().isoformat()}_{datetime.now().time().isoformat(timespec="seconds")}_log.json")
    def download_log_obj():
        logs = logs_attr.get()
        if not logs:
            yield json.dumps({"error": "No logs collected yet"}, indent=4)
        else:
            yield json.dumps(logs, indent=4)
