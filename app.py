########################
#Imports
########################

import seaborn as sns
from faicons import icon_svg
from pathlib import Path
import pandas as pd
from shiny import reactive
from shiny.express import input, render, ui

########################
#Load Data 
########################

# Load the dataset at the global level

data_path = Path(__file__).parent / "KCPD_Crime_Data_2024_20241202.csv"
df = pd.read_csv(data_path)

########################
#User Interface 
########################

ui.page_opts(title="Crime Reports Dashboard", fillable=True)
# Add a subtitle below the main title


ui.h3("An interactive dashboard for analyzing crime reports in KC from September to November of 2024", class_="subtitle")


# Sidebar controls for filtering
with ui.sidebar(title="Filters"):
    ui.input_slider("age", "Max Age Of Reporter:", min(df["Age"]), max(df["Age"]), max(df["Age"]))
    
    #Select Offense
    ui.input_selectize(
        "offense",
        "Click to Select Offense Type:",
        list(df["Offense"].unique()),  
        selected=[],
        multiple=True,
    )

    #Dropdown for gender filter
    ui.input_checkbox_group(
        "gender",
        "Gender",
        choices=["M", "F"],  # Add gender options
        selected=[]  # Start with no selection
    )


# Display summary value boxes
with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("file")):
        "Number of Reports"

        @render.text
        def report_count():
            return filtered_df().shape[0]

    with ui.value_box(showcase=icon_svg("clock")):
        "Average Age of Victims"

        @render.text
        def average_age():
            return f"{filtered_df()['Age'].mean():.1f} years"

    with ui.value_box(showcase=icon_svg("flag")):
        "Number of Unique Offenses"

        @render.text
        def unique_offenses():
            return filtered_df()["Offense"].nunique()


# Display charts and data table
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Age Distribution by Sex")
        
        @render.plot
        def age_distribution():
            return sns.boxplot(
                data=filtered_df(),
                x="Sex",
                y="Age",
                palette="Set3",
            )


    with ui.card(full_screen=True):
        ui.card_header("Crime Data Table")

        @render.data_frame
        def crime_data():
            cols = [
                "Offense",
                "Address",
                "Age",
                "Sex",
                "Race",
                "Reported_Date",
            ]
            return render.DataGrid(filtered_df()[cols], filters=True)


# Define reactive filtered data
@reactive.calc
def filtered_df():
    # Get selected offenses, months, and gender
    selected_offenses = input.offense()
    selected_gender = input.gender()
    
    # Start with the full dataset
    filt_df = df
    
    # Filter by selected offenses (if any)
    if selected_offenses:
        filt_df = filt_df[filt_df["Offense"].isin(selected_offenses)]
    
    # Filter by selected gender (if any)
    if selected_gender:
        filt_df = filt_df[filt_df["Sex"].isin(selected_gender)]
    
    # Filter by age
    filt_df = filt_df.loc[filt_df["Age"] <= input.age()]
    
    return filt_df

# Include custom CSS
ui.include_css(Path(__file__).parent / "styles.css")
