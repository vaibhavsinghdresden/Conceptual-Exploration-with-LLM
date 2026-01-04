from shiny import App, reactive, render, ui, module

from additional_functionality.input_data_and_set_context_object import context_upload_ui,context_upload_server

from attribute_exploration.context_display import context_display_attr_exp_ui, context_display_attr_exp_server
from attribute_exploration.attr_exp_manual_mode import attr_exp_manual_mode_ui,attr_exp_manual_mode_server
from attribute_exploration.attr_exp_assisted_mode import attr_exp_assisted_mode_ui,attr_exp_assisted_mode_server
from attribute_exploration.attr_exp_auto_mode import attr_exp_auto_mode_ui,attr_exp_auto_mode_server

from object_exploration.context_display_obj import context_display_obj_exp_ui,context_display_obj_exp_server
from object_exploration.obj_exp_manual_mode import obj_exp_manual_mode_ui,obj_exp_manual_mode_server
from object_exploration.obj_exp_assisted_mode import obj_exp_assisted_mode_ui,obj_exp_assisted_mode_server
from object_exploration.obj_exp_auto_mode import obj_exp_auto_mode_ui,obj_exp_auto_mode_server

app_ui = ui.page_fluid(
    ui.tags.head(
            ui.tags.link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
            )
        ),
    ui.tags.style("""
        html, body {
            height: 100%;
            padding: 15px;
            background-color: black;
            color: white;
        }
        #check {
            height: 100%;
        }
    """),
    ui.h1("LINGUISTIC CONCEPT ANALYSIS USING LLM", style="text-align: center;padding: 10px;"),
    ui.navset_pill(
        ui.nav_panel("Input File",context_upload_ui("context_upload"),),
        ui.nav_panel("Attribute Exploration",
                    ui.layout_columns(
                        ui.card(
                            ui.h2("Attribute Exploration", style="text-align: center;"),
                            ui.navset_pill(
                                ui.nav_panel("Manual Mode",attr_exp_manual_mode_ui("attr_exp_manual_mode"),),
                                ui.nav_panel("Assisted Mode",attr_exp_assisted_mode_ui("attr_exp_assisted_mode")),
                                ui.nav_panel("Automated Mode",attr_exp_auto_mode_ui("attr_exp_auto_mode")),
                                id="tab",
                            ),
                        ),
                        ui.card(
                            context_display_attr_exp_ui("context_display_attr_exp"),
                            style="height: 100vh; overflow-y: auto;"
                        ),
                        col_widths=(6, 6),
                        style="margin-top: 20px;"
                    ),
        ),
        ui.nav_panel("Object Exploration",
            ui.layout_columns(
                ui.card(
                    ui.h2("Object Exploration", style="text-align: center;"),
                    ui.navset_pill(
                            ui.nav_panel("Manual Mode", obj_exp_manual_mode_ui("obj_exp_manual_mode")),
                            ui.nav_panel("Assisted Mode", obj_exp_assisted_mode_ui("obj_exp_assisted_mode")),
                            ui.nav_panel("Automated Mode", obj_exp_auto_mode_ui("obj_exp_auto_mode")),
                            ),
                        style="height: 100vh; overflow-y: auto;"
                    ),
                ui.card(context_display_obj_exp_ui("context_display_obj_exp")),
                col_widths=(6, 6),
                style="margin-top: 20px;"
                ),
            ),
        ui.nav_control(ui.input_action_button("reload_btn", "Reset",class_ ="btn btn-outline-danger", style="margin-left: 20px;"),),
        id="page",
    ),
    ui.tags.script("""
                   document.getElementById("reload_btn").onclick = function() {
                       location.reload();
                   };
       """),
    style = "height: 100vh; overflow-y: auto;"
)

def server(input, output, session):
    context_obj_state = reactive.value(None)
    trigger_recalc = reactive.Value(0)
    selected_implication_index = reactive.value(0)
    selected_obj_implication_index = reactive.value(0)

    context_upload_server(id="context_upload",cxt=context_obj_state, trigger_recalc=trigger_recalc)

    attr_exp_manual_mode_server(id="attr_exp_manual_mode",cxt=context_obj_state, trigger_recalc=trigger_recalc, selected_attr_index=selected_implication_index)
    attr_exp_assisted_mode_server(id="attr_exp_assisted_mode",cxt=context_obj_state, trigger_recalc=trigger_recalc, selected_attr_index=selected_implication_index)
    attr_exp_auto_mode_server(id="attr_exp_auto_mode",cxt=context_obj_state, trigger_recalc=trigger_recalc)
    context_display_attr_exp_server(id="context_display_attr_exp",cxt=context_obj_state, trigger_recalc=trigger_recalc, selected_attr_index=selected_implication_index)

    obj_exp_manual_mode_server(id="obj_exp_manual_mode",cxt=context_obj_state, trigger_recalc=trigger_recalc, selected_obj_index=selected_obj_implication_index)
    obj_exp_assisted_mode_server(id="obj_exp_assisted_mode",cxt=context_obj_state, trigger_recalc=trigger_recalc,selected_obj_index=selected_obj_implication_index)
    obj_exp_auto_mode_server(id="obj_exp_auto_mode",cxt=context_obj_state, trigger_recalc=trigger_recalc)
    context_display_obj_exp_server(id="context_display_obj_exp", cxt=context_obj_state, trigger_recalc=trigger_recalc,selected_obj_index=selected_obj_implication_index)

app = App(app_ui, server)
