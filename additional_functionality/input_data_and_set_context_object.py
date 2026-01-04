from shiny import App, reactive, render, ui, module
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from exploration import Explorer
import re

@module.ui
def context_upload_ui():
    return ui.card(ui.div(
                     ui.h5("Input File :",
                           style="""
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    margin-bottom: 30px;
                                    margin-top: 20px;
                                """
                           ),
                     ui.div(
                         ui.input_file("file", "", accept=[".xlsx", ".xls", ".cxt", ".csv"]),
                         style="""
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 50px;
                                    margin-bottom: 30px;
                                """
                        ),
                     ),
                     ui.output_ui("render_upload_instructions"),
                     ui.output_ui("render_row_col_selectors"),
                     ui.output_ui("render_context_confirmation_text"),
                     ui.output_data_frame("render_dataframe"),
                        style="height: 100vh; overflow-y: auto; margin-top: 20px;",
                     )


@module.server
def context_upload_server(input, output, session, cxt, trigger_recalc):
    object_context_dimensions = reactive.value(None)
    confirm_context_text = reactive.value(False)

    @reactive.calc
    def get_input_dataframe():
        file = input.file()
        if not file:
            return None
        else:
            if file[0]['name'][-4:] == "xlsx" or file[0]['name'][-4:] == "xls":
                return pd.read_excel(file[0]['datapath'], index_col=0)

            elif file[0]['name'][-4:] == ".csv":
                df = pd.read_csv(file[0]['datapath'], index_col=0)
                df = df.map(lambda x: True if x == "X" else False)
                return df.T

            elif file[0]['name'][-4:] == ".cxt":
                input_file = open(file[0]['datapath'], "r")
                assert input_file.readline().strip() == "B", \
                    "File is not valid cxt"
                input_file.readline()  # Empty line
                number_of_objects = int(input_file.readline().strip())
                number_of_attributes = int(input_file.readline().strip())
                input_file.readline()  # Empty line

                objects = [input_file.readline().strip() for i in range(number_of_objects)]
                attributes = [input_file.readline().strip() for i in range(number_of_attributes)]

                table = []
                for i in range(number_of_objects):
                    line = [c == "X" for c in input_file.readline().strip()]
                    table.append(line)

                table_np = np.array(table)
                table_np = table_np.T

                input_file.close()
                return pd.DataFrame(table_np, index=attributes, columns=objects)

            else:
                return None

    @output
    @render.ui
    def render_upload_instructions():
        df = get_input_dataframe()
        if df is None:
            return ui.div(
                ui.div(
                    ui.markdown(
                        """
                        ✅ **Supported file formats**:
                        - `.csv`
                        - `.cxt`
                        - `.xls`
                        - `.xlsx`

                        📌 **File Format Requirements**:
                        - For the **excel file**, The **first column** should contain the **frames**.
                        - Each **subsequent column** should contain a **verb** followed by the True/False values.
                        - For best results in **Assisted and Auto Mode**, include a column titled **"Example"** with explanations for each frame.
                        """
                    ),
                ),
                style="""
                                display: flex;
                                justify-content: center;
                                # align-items: center;
                                height: 50px;
                                margin-bottom: 30px;
                            """
            )
        else:
            return None

    @output
    @render.ui
    def render_row_col_selectors():
        df = get_input_dataframe()
        if df is not None:
            if 'Example' in df.columns:
                df = df.drop(['Example'], axis=1)
            rows, columns = df.shape

            return ui.layout_columns(
                ui.div(
                    ui.h6("Select Rows"),
                    ui.input_slider("row_slider", "", min=1, max=rows, value=[1, 4], ),
                    style="display: flex; flex-direction: column; align-items: center;",
                ),
                ui.div(
                    ui.h6("Select Column", style="text-align: center;"),
                    ui.input_slider("column_slider", "", min=1, max=columns, value=[1, 4]),
                    style="display: flex; flex-direction: column; align-items: center;"
                ),
                ui.div(
                    ui.input_action_button("confirm_context", "confirm context", class_="btn-success",
                                           style="margin-top: 20px;", ),
                ),
                col_widths=(5, 5, 2),
            )
        else:
            return ui.div("")

    @output
    @render.data_frame
    def render_dataframe():
        df = get_input_dataframe()
        if df is not None:
            if 'Example' in df.columns:
                df = df.drop(['Example'], axis=1)
            start_col, end_col = 1, 4
            start_row, end_row = 1, 4
            if input.row_slider():
                start_row, end_row = input.row_slider()
            if input.row_slider():
                start_col, end_col = input.column_slider()

            object_context_dimensions.set([start_col, end_col, start_row, end_row])

            df_reset = df.reset_index()
            return df_reset.iloc[start_row - 1:end_row, np.r_[0, start_col:end_col + 1]]
        else:
            return pd.DataFrame()

    @reactive.calc
    @reactive.event(input.confirm_context)
    def get_selected_context_data():
        if input.confirm_context():
            df = get_input_dataframe()
            attributes = []
            objects = []
            values = []
            examples = []
            if not df.empty:
                confirm_context_text.set(True)
                if 'Example' in df.columns:
                    examples = df.loc[:, 'Example']
                    examples = examples.to_list()
                    df = df.drop(['Example'], axis=1)
                else:
                    examples = list(" " * df.shape[0])

                df = df.transpose()
                ll = object_context_dimensions.get()
                start_col, end_col, start_row, end_row = ll

                df = df.iloc[start_col - 1:end_col, start_row - 1:end_row]  # taking out english

                df.columns = df.columns.map(lambda x: x.replace(",", " or") if isinstance(x, str) else x)
                # df.index = df.index.map(lambda x: x.replace("English: ", "") if isinstance(x, str) else x)
                # df.index = df.index.map(
                #     lambda x: re.sub(r"^[A-Za-z]+:\s*", "", x) if isinstance(x, str) else x
                # )
                objects = list(o.strip() for o in df.index)
                objects = [re.sub(r"\s*:\s*", ":", s) for s in objects]
                attributes = list(a.strip() for a in df.columns)

                values = df.values
                values = values.tolist()


            return attributes, objects, values, examples
        else:
            return None, None, None, None

    @output
    @render.ui
    def render_context_confirmation_text():
        if confirm_context_text.get():
            a = "The context has been successfully configured. You may proceed with the explorations."
            b = ui.h6(f'{a}', style="color: Green; text-align: center; font-weight: bold;")
            return b
        else:
            return ui.div("")

    @reactive.effect
    def initialize_explorer_object():
        attributes, objects, values, examples = get_selected_context_data()
        if objects is not None:
            context = Explorer(values, objects, attributes)
            context.Basic_Exploration.set_context_data(values, examples)
            cxt.set(context)