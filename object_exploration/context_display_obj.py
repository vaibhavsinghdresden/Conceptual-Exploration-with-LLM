from shiny import App, reactive, render, ui, module
from calendar import prmonth
import random
from datetime import date

@module.ui
def context_display_obj_exp_ui():
    return ui.div( 
                    ui.h2("Context Output", style="text-align: center;"),
                    ui.div(
                                ui.output_data_frame("render_context_object"),
                            ),
                    ui.layout_columns(
                                ui.card(
                                    ui.h6("Active Object Implications", style="text-align: center;"),
                                    ui.output_ui("render_all_active_object_implications"),
                                ),
                                ui.card(
                                    ui.h6("Confirmed Object Implications", style="text-align: center;"),
                                    ui.output_ui("render_confirmed_object_implications"),
                                ),
                                col_widths=(6, 6)
                            ),
                    ui.layout_columns(
                            ui.h1(),
                            ui.download_button("download_df_object", "Download Context CSV",
                                               class_="btn btn-outline-primary",
                                               style="text-align: center; font-size: 12px; width: 190px;"),
                            ui.download_button("download_cxt_object", "Download Context CSV",
                                           class_="btn btn-outline-primary",
                                           style="text-align: center; font-size: 12px; width: 190px;"),
                            ui.h1(),
                            col_widths=(2,4,4,2)
                            ),
                    style="height: 90vh; overflow-y: auto;"
                ),



@module.server
def context_display_obj_exp_server(input, output, session, cxt, trigger_recalc, selected_obj_index):
    @output
    @render.data_frame
    def render_context_object():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            df = context.Basic_Exploration.get_context_dataframe()
            df_display = df.copy()
            # df_display.columns = [col[:3] + "..." if len(col) > 13 else col for col in df.columns]
            df_reset = df_display.reset_index()
            return df_reset
        return None
        # return pd.DataFrame()

    @output
    @render.ui
    def render_all_active_object_implications():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_object_implications()
            i = 0
            imp_dict = {}
            for imp in implication:
                imp_dict[f"{i}"] = f'{imp}'
                i = i + 1
            if not imp_dict:
                return ui.div("")
            else:
                return ui.div(
                    ui.input_radio_buttons(
                        "radio_imp_attr_obj",
                        "",
                        imp_dict,
                    ),
                )
        return ui.div("")

    @reactive.effect
    @reactive.event(input.radio_imp_attr_obj)
    def select_attribute_value_object():
        selected_obj_index.set(int(input.radio_imp_attr_obj()))

    @output
    @render.ui
    def render_confirmed_object_implications():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_confirmed_object_implications()
            return ui.div(
                *[ui.h6(f'{imp}') for imp in implication]
            )
        return ui.div("")

    @output
    @render.download(filename=lambda: f"context_csv_{date.today().isoformat()}_{datetime.now().time().isoformat(timespec="seconds")}.csv")
    def download_df_object():
        context = cxt.get()
        if context is None:
            d = {'THE DATAFRAME IS EMPTY': ['PLEASE SET THE CONTEXT FIRST']}
            df = pd.DataFrame(data=d)
            yield df.to_csv()
        else:
            df = context.Basic_Exploration.get_context_dataframe()
            yield df.to_csv()

    @output
    @render.download(filename=lambda: f"context_cxt_{date.today().isoformat()}_{datetime.now().time().isoformat(timespec="seconds")}.cxt")
    def download_cxt_object():
        context = cxt.get()
        if context is None:
            cxt = "the context is not set"
            yield cxt
        else:
            cxt = context.Basic_Exploration.get_context_cxt()
            yield cxt