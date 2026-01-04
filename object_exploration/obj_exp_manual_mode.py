from shiny import App, reactive, render, ui, module

@module.ui
def obj_exp_manual_mode_ui():
    return ui.card(
                 ui.div(
                    ui.output_ui("render_current_object_implication_output"),
                    ui.layout_columns(
                        ui.h3(""),
                        ui.output_ui("render_start_manual_mode_button_object"),
                        ui.output_ui("render_object_implication_action_button"),
                        ui.h3(""),
                        col_widths=(1,5,5,1),
                    ),
                    ui.output_ui("render_object_implication_message_output"),
                    style="padding-top: 30px; background-color: white; color: black;"
                 ),
            ),

@module.server
def obj_exp_manual_mode_server(input, output, session, cxt, trigger_recalc, selected_obj_index):
    implication_message_object = reactive.value(None)
    toggle_state_object = reactive.Value(True)

    @output
    @render.ui
    def render_current_object_implication_output():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_current_object_implications(selected_obj_index.get())
            return ui.div(
                ui.strong(f"Current Implication : {implication}"),
                style="text-align: center; margin-top: 20px; margin-bottom: 30px;",
            )
        return ui.div("")

    @output
    @render.ui
    def render_start_manual_mode_button_object():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file.", style="color: red;"),
            )
        else:
            return ui.input_action_button("confirm_implication_object", "confirm implication", class_="btn-success",
                                          style="margin-top: 20px;width: 250px;", ),

    @output
    @render.ui
    def render_object_implication_message_output():
        a = implication_message_object.get()
        if a is not None:
            a = implication_message_object.get()
            return ui.div(a)
        else:
            return ui.div("")

    @output
    @render.ui
    def render_object_implication_action_button():
        context = cxt.get()
        if context is not None:
            if toggle_state_object():
                return ui.input_action_button(
                    "toggle_button_object", "reject implication",
                    class_="btn-warning", style="margin-top: 20px; width: 250px;",
                )
            else:
                return ui.input_action_button(
                    "toggle_button_object", "confirm counter example",
                    class_="btn-primary", style="margin-top: 20px; width: 250px;"
                )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.confirm_implication_object)
    def handle_confirm_object_implication():
        if input.confirm_implication_object():
            trigger_recalc.set(trigger_recalc.get() + 1)
            context = cxt.get()
            if context is not None:
                toggle_state_object.set(True)
                context.Basic_Exploration.post_confirm_object_implications(selected_obj_index.get())
                txt = "Previous Implication Confirmed."
                msg = ui.h6(f'{txt}', style="color: Green; text-align: center; font-weight: bold;")
                implication_message_object.set(msg)
        else:
            implication_message_object.set("")

    @reactive.effect
    @reactive.event(input.toggle_button_object)
    def handle_toggle_button_click():
        if toggle_state_object():
            trigger_recalc.set(trigger_recalc.get() + 1)
            _, objects, _, _ = context_data()
            msg = ui.div(
                ui.h6(f'Implication Rejected',
                      style="color: Red; text-align: center; font-weight: bold; margin-top: 20px;"),
                ui.h6(f'Provide Counter Example below',
                      style="color: Black; text-align: center; margin-top: 20px; margin-bottom: 20px;"),
                ui.layout_columns(
                    ui.div(
                        ui.h6("Enter Counter Object", style="margin-bottom: 20px;"),
                        ui.input_text("counter_object_text_object", "", "object"),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.div(
                        ui.h6("Enter Counter Object's Attributes", style="margin-bottom: 20px;"),
                        ui.input_checkbox_group(  # <<
                            "counter_attribute_checkbox_object",  # <<
                            "",
                            objects,
                        ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                ),
            )
            implication_message_object.set(msg)

        else:
            try:
                context = cxt.get()
                counter_object = input.counter_object_text_object()
                counter_attributes = input.counter_attribute_checkbox_object()

                out = context.Basic_Exploration.set_counter_example_object(counter_object, counter_attributes,
                                                                       selected_obj_index.get())

                if out[0] == "PASS":
                    trigger_recalc.set(trigger_recalc.get() + 1)
                    a = "Previous Counter Example has been Confirmed."
                    msg = ui.h6(f'{a}', style="color: Blue; text-align: center; font-weight: bold;")
                    implication_message_object.set(msg)

                if out[0] == "FAIL":
                    a = "Counter Example is invalid."
                    msg = ui.div(
                        ui.h6(f'{a}', style="color: Red; text-align: center; font-weight: bold;"),
                        ui.h6(f'{out[1]}', style="color: Red; text-align: center; font-weight: bold;")
                    )
                    implication_message_object.set(msg)
            except Exception as e:
                pass
        toggle_state_object.set(not toggle_state_object())
