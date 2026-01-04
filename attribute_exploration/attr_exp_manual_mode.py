from shiny import App, reactive, render, ui, module

@module.ui
def attr_exp_manual_mode_ui():
    return ui.card(
                     ui.div(
                        ui.output_ui("render_current_implication_output"),
                        ui.layout_columns(
                            ui.h3(""),
                            ui.output_ui("render_start_manual_mode_button"),
                            ui.output_ui("render_implication_action_button"),
                            ui.h3(""),
                            col_widths=(1,5,5,1),
                        ),
                        ui.output_ui("render_implication_message_output"),
                        style="padding-top: 30px; background-color: white; color: black;"
                    ),
                )

@module.server
def attr_exp_manual_mode_server(input, output, session, cxt, trigger_recalc, selected_attr_index):
    implication_message = reactive.value(None)
    toggle_state = reactive.Value(True)

    @output
    @render.ui
    def render_current_implication_output():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_current_implications(selected_attr_index.get())
            return ui.div(
                ui.strong(f"Current Implication : {implication}"),
                style="text-align: center; margin-top: 20px; margin-bottom: 30px;",
            )
        return ui.div("")

    @output
    @render.ui
    def render_start_manual_mode_button():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file.", style="color: red;"),
            )
        else:
            return ui.input_action_button("confirm_implication", "confirm implication", class_="btn-success",
                                          style="margin-top: 20px;width: 250px;", ),

    @output
    @render.ui
    def render_implication_action_button():
        context = cxt.get()
        if context is not None:
            if toggle_state():
                return ui.input_action_button(
                    "toggle_button", "reject implication",
                    class_="btn-warning", style="margin-top: 20px; width: 250px;",
                )
            else:
                return ui.input_action_button(
                    "toggle_button", "confirm counter example",
                    class_="btn-primary", style="margin-top: 20px; width: 250px;"
                )
        else:
            return ui.div("")

    @output
    @render.ui
    def render_implication_message_output():
        a = implication_message.get()
        if a is not None:
            a = implication_message.get()
            return ui.div(a)
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.confirm_implication)
    def handle_confirm_implication():
        if input.confirm_implication():
            trigger_recalc.set(trigger_recalc.get() + 1)
            context = cxt.get()
            if context is not None:
                toggle_state.set(True)
                context.Basic_Exploration.post_confirm_implications(selected_attr_index.get())
                a = "Previous Implication Confirmed."
                b = ui.h6(f'{a}', style="color: Green; text-align: center; font-weight: bold;")
                implication_message.set(b)
        else:
            implication_message.set("")

    @reactive.effect
    @reactive.event(input.toggle_button)
    def handle_toggle_action():
        if toggle_state():
            context = cxt.get()
            trigger_recalc.set(trigger_recalc.get() + 1)
            attributes = context.Basic_Exploration.attributes

            form_ui = ui.div(
                ui.h6(f'Implication Rejected', style="color: Red; text-align: center; font-weight: bold; margin-top: 20px;"),
                ui.h6(f'Provide Counter Example below', style="color: Black; text-align: center; margin-top: 20px; margin-bottom: 20px;"),
                ui.layout_columns(
                    ui.div(
                        ui.h6("Enter Counter Object",style="margin-bottom: 20px;"),
                        ui.input_text("counter_object_text", "", "object"),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.div(
                        ui.h6("Enter Counter Object's Attributes",style="margin-bottom: 20px;" ),
                        ui.input_checkbox_group(  # <<
                            "counter_attribute_checkbox",  # <<
                            "",
                            attributes,
                        ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                ),
            )
            implication_message.set(form_ui)

        else:
            try:
                context = cxt.get()
                counter_object = input.counter_object_text()
                counter_attributes = input.counter_attribute_checkbox()
                objects = context.Basic_Exploration.get_current_objects()
                if counter_object in objects :
                    msg = ui.div(
                        ui.h6(f'Counter Example is Invalid', style="color: Red; text-align: center; font-weight: bold;"),
                        ui.h6(f'Object with the name "{counter_object}" already present in the context.',
                              style="color: Red; text-align: center; font-weight: bold;")
                    )
                    implication_message.set(msg)
                else:
                    out = context.Basic_Exploration.set_counter_example(counter_object, counter_attributes, selected_attr_index.get())
                    if out[0] == "PASS":
                        trigger_recalc.set(trigger_recalc.get() + 1)
                        msg = ui.h6(f'Previous Counter Example has been Confirmed.', style="color: Blue; text-align: center; font-weight: bold;")
                        implication_message.set(msg)
                    if out[0] == "FAIL":
                        msg = ui.div(
                            ui.h6(f'Counter Example is Invalid.', style="color: Red; text-align: center; font-weight: bold;"),
                            ui.h6(f'{out[1]}', style="color: Red; text-align: center; font-weight: bold;")
                        )
                        implication_message.set(msg)
            except Exception as e:
                pass
        toggle_state.set(not toggle_state())