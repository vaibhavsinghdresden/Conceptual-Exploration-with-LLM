from shiny import App, reactive, render, ui, module
from calendar import prmonth
import random
from datetime import date, datetime

@module.ui
def context_display_attr_exp_ui():
    return ui.div(
                    ui.h2("Context Output", style="text-align: center;"),
                    ui.div(
                        ui.output_data_frame("render_context"),
                    ),
                    ui.layout_columns(
                        ui.card(
                            ui.h6("Active Attr Implications", style="text-align: center;"),
                            ui.output_ui("render_all_active_implication"),
                        ),
                        ui.card(
                            ui.h6("Confirmed Attr Implications", style="text-align: center;"),
                            ui.output_ui("render_confirmed_implication"),
                        ),
                        col_widths=(6, 6)
                    ),
                    ui.layout_columns(
                            ui.h1(),
                            ui.download_button("download_df", "Download Context CSV", class_="btn btn-outline-primary",style="text-align: center; font-size: 12px; width: 190px;"),
                            ui.download_button("download_cxt", "Download Context CXT", class_="btn btn-outline-primary",style="text-align: center; font-size: 12px; width: 190px;"),
                            ui.h1(),
                            col_widths=(2,4, 4,2)
                            ),
                    style="height: 100vh; overflow-y: auto;"
            ),

@module.server
def context_display_attr_exp_server(input, output, session, cxt, trigger_recalc, selected_attr_index):
    @output
    @render.data_frame
    def render_context():
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
    def render_all_active_implication():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_attribute_implications()
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
                        "radio_imp_attr",
                        "",
                        imp_dict,
                    ),
                )
        return ui.div("")

    @reactive.effect
    @reactive.event(input.radio_imp_attr)
    def handle_implication_selection():
        selected_attr_index.set(int(input.radio_imp_attr()))

    @output
    @render.ui
    def render_confirmed_implication():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_confirmed_implications()
            return ui.div(
                *[ui.h6(f'{imp}') for imp in implication]
            )
        return ui.div("")

    @output
    @render.download(filename=lambda: f"context_csv_{date.today().isoformat()}_{datetime.now().time().isoformat(timespec="seconds")}.csv")
    def download_df():
        context = cxt.get()
        if context is None:
            message = "The context is not set"
            yield message
        else:
            df = context.Basic_Exploration.get_context_dataframe()
            yield df.to_csv()

    @output
    @render.download(filename=lambda: f"context_cxt_{date.today().isoformat()}_{datetime.now().time().isoformat(timespec="seconds")}.cxt")
    def download_cxt():
        context = cxt.get()
        if context is None:
            message = "The context is not set"
            yield message
        else:
            cxt_file = context.Basic_Exploration.get_context_cxt()
            yield cxt_file