import sqlite3
import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import Toplevel
from tkinter import filedialog
from tkinter import simpledialog
import webbrowser
from google_images_search import GoogleImagesSearch
import requests
from io import BytesIO
from PIL import Image, ImageTk, UnidentifiedImageError
import csv
from ttkthemes import ThemedStyle
import math
import os


# initial paramaters
database_path = "car_database.db"
# table_names = get_table_names(database_path)
table_names = "car_db_metric"

# Google Cloud Console Developer API Keys:
# These can be acquired for free and offer more daily usage 
#   than a single user would ever need within the scope of this program
GCS_DEVELOPER_KEY = 'INSERT KEY'
GCS_CX = 'INSERT KEY'

# Create a GoogleImagesSearch object
gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

# makes an array with all the variable names, and certain flags will be added later for advanced or basic variables,
#   turning it into a 2D array
variable_names = [
    "Make: ",
    "Model: ",
    "Generation: ",
    "From Year: ",
    "To Year: ",
    "Car Series: ",
    "Trim: ",
    "Body Type: ",
    "Load Height (mm): ",
    "Number of Seats: ",
    "Length (mm): ",
    "Width (mm): ",
    "Height (mm): ",
    "Wheelbase (mm): ",
    "Front Track (mm): ",
    "Rear Track (mm): ",
    "Curb Weight (kg): ",
    "Wheel Size (r14): ",
    "Ground Clearance (mm): ",
    "Trailer Load with Brakes (kg): ",
    "Payload (kg): ",
    "Back Track Width (mm): ",
    "Front Track Width (mm): ",
    "Clearance (mm): ",
    "Full Weight (kg): ",
    "Front Rear Axle Load (kg): ",
    "Max Trunk Capacity (liters): ",
    "Cargo Compartment Length Width Height (mm): ",
    "Cargo Volume (m3): ",
    "Minimum Trunk Capacity (liters): ",
    "Maximum Torque (N*m): ",
    "Turnover of Maximum Torque (rpm): ",
    "Injection Type: ",
    "Overhead Camshaft: ",
    "Cylinder Layout: ",
    "Number of Cylinders: ",
    "Compression Ratio: ",
    "Engine Type: ",
    "Valves per Cylinder: ",
    "Boost Type: ",
    "Cylinder Bore (mm): ",
    "Stroke Cycle (mm): ",
    "Engine Placement: ",
    "Cylinder Bore and Stroke Cycle (mm): ",
    "Max Power (kW): ",
    "Presence of Intercooler: ",
    "Engine Displacement (cm3): ",
    "Engine HP: ",
    "Engine HP RPM: ",
    "Drive Wheels: ",
    "Bore Stroke Ratio: ",
    "Number of Gears: ",
    "Turning Circle (m): ",
    "Transmission: ",
    "Mixed Fuel Consumption per 100 km (l): ",
    "Range (km): ",
    "Emission Standards: ",
    "Fuel Tank Capacity (l): ",
    "Acceleration 0-100 km/h (s): ",
    "Max Speed (km/h): ",
    "City Fuel per 100 km (l): ",
    "CO2 Emissions (g/km): ",
    "Fuel Grade: ",
    "Highway Fuel per 100 km (l): ",
    "Back Suspension: ",
    "Rear Brakes: ",
    "Front Brakes: ",
    "Front Suspension: ",
    "Steering Type: ",
    "Car Class: ",
    "Country of Origin: ",
    "Number of Doors: ",
    "Safety Assessment: ",
    "Rating Name: ",
    "Battery Capacity (KW/h): ",
    "Electric Range (km): ",
    "Charging Time (h): "
    ]

# List of car categories and corresponding keywords
car_body_categories = {
    "Roadster": ["Roadster", "Speedster"],
    "Coupe": ["Coupe", "Fastback", "Hardtop"],
    "Hatchback": ["Hatchback", "Liftback"],
    "Spyder": ["Spyder", "Spider"],
    "Cabriolet": ["Cabriolet"],
    "Sedan": ["Sedan", "Targa"],
    "Wagon": ["Wagon"],
    "SUV": ["SUV", "Crossover"],
    "Pickup": ["Pickup"],
    "Van": ["Van", "Minivan"],
    "Limousine": ["Limousine"],
    }

Basic_variable_names = ["Make: ", "Model: ", "From Year: ", "To Year: ", "Car Series: ", "Trim: ", "Curb Weight (kg): ",
                        "Full Weight (kg): ", "Engine HP: ", "Transmission: "]
# Turns the variable_names list into a 2D array, marking the Basic_Variable_Names which are shown in simple searches
#   as to not overwhelm the user
for i, g in enumerate(variable_names):
    if g in Basic_variable_names:
        variable_names[i] = [g, True]
    else:
        variable_names[i] = [g, False]


# Method to check if the SQL database is accessible and readable by the operating system using the sqlite3 and os libraries
# Returns True for valid access, False for error
def is_valid_sqlite3_database(file_path):
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        cursor.fetchall()
        conn.close()
        # Check if the file has read access
        if os.access(file_path, os.R_OK):
            # print("Read access is granted.")
            return True
        else:
            print("Read access is denied.")
    except sqlite3.DatabaseError:
        return False


# Is used on GUI creation to apply a clean, modern GUI theme to Tkinter using the ttkthemes library
def apply_ttk_theme():
    style = ThemedStyle(TkinterRoot)
    style.set_theme('clam')


# Method to categorize car models based on keywords
# Used in the program to search cars by keywords such as "Coupe" or "Hatchback", used in "sort_car_series_column_by_keywords"
def categorize_model(model_name, categories):
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in model_name.lower():
                return category
    return None


# Method to sort and categorize car series column in the database
# Returns a 2D array of all the cars that fit under a certain keyword
def sort_car_series_column_by_keywords(database_path, table_name, categories):
    try:
        results = {}
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()

            # Select car series column from the database
            cursor.execute(f"SELECT DISTINCT series FROM {table_name}")
            car_series_rows = cursor.fetchall()

            # Create an empty dictionary to store categorized models
            categorized_models = {category: [] for category in categories}

            # Iterate through the car series rows and categorize the models
            for row in car_series_rows:
                car_series = row[0]
                category = categorize_model(car_series, categories)
                if category:
                    categorized_models[category].append(car_series)

            # Store the categorized models in the 'results' dictionary
            for category, models in categorized_models.items():
                results[category] = models

        # print(results)
        return results  # Return the results as a dictionary

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return {}  # Return an empty dictionary in case of an error


# Method takes a brand and shows all the models under said brand, used to help the user find models after selecting their brand,
#   This is because (at time of writing) the 68,000 unique models in the database are overwhelming to look at
# Returns the unique models of the chosen brand (make)
def search_by_brand_show_model_only(database_path, table_name, brand_string):
    try:
        with sqlite3.connect(database_path) as connection:
            # Connects to the SQL database
            # Creates a cursor to interact with the database
            cursor = connection.cursor()
            # strip leading and trailing whitespace from seaerch words
            brand_list = [brand.strip() for brand in brand_string.split(',')]
            model_list = []
            # Constructs a search query for the database
            # Distinct means that only unique models are chosen
            search_query = f"SELECT DISTINCT model FROM {table_name} WHERE make IN ({','.join(['?'] * len(brand_list))})"
            # Executes the search query
            cursor.execute(search_query, brand_list)
            # fetches all matching rows
            rows = cursor.fetchall()
            if len(rows) > 0:
                # print("Column Names:", column_names)
                # Puts them in a set, sets ignore any duplicates automatically
                unique_models = set()
                # print each matching row
                for row in rows:
                    unique_models.add(row[0])
                else:
                    # Uncomment for debugging purposes
                    # print("Finished search")
                    pass
                # the sorted command automatically sorts them alphanumerically
                for model in sorted(unique_models):
                    model_list.append(model)
                    # print(model)

            return model_list

    except sqlite3.Error as e:
        print("An error occured:", e)
    return []


# Returns either the min or the max year in the database out of all the cars based on the min_max_flag
def get_min_max_year(database_path, table_names, min_max_flag):
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = (f"SELECT MIN(year_from) FROM {table_names}")
            elif min_max_flag == "max":
                search_query = (f"SELECT MAX(year_to) FROM {table_names}")
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                return round(result[0])
    except sqlite3.Error as e:
        print("An error occurred while fetching min and max years:", e)
        return 1000


# The following method do the same thing as get_min_max_year, but with different data points
# Data returned by the method is self-explanatory in the method's name
def get_min_max_seating_capacity(min_max_flag, database_path, table_names):
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = f"SELECT MIN(number_of_seats) FROM {table_names}"
            elif min_max_flag == "max":
                search_query = f"SELECT MAX(number_of_seats) FROM {table_names}"
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                seats_num = result[0]
                # Split the string by commas and convert the parts to integers
                numbers = [int(number.strip()) for number in seats_num.split(',')]
                # Find the maximum number among the extracted integers
            if min_max_flag == "min":
                return min(numbers)
            elif min_max_flag == "max":
                return max(numbers)
    except sqlite3.Error as e:
        print("An error occurred while fetching min and max years:", e)
        return 1


def get_min_max_engine_hp(min_max_flag, database_path, table_names):
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = (f"SELECT MIN(engine_hp) FROM {table_names}")
            elif min_max_flag == "max":
                search_query = (f"SELECT MAX(engine_hp) FROM {table_names}")
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                return result[0]
    except sqlite3.Error as e:
        print("An error occurred while fetching min and max years:", e)
        return 0


def get_min_max_curb_weight(min_max_flag, database_path, table_names):
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = (f"SELECT MIN(curb_weight_kg) FROM {table_names}")
            elif min_max_flag == "max":
                search_query = (f"SELECT MAX(curb_weight_kg) FROM {table_names}")
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                return result[0]
    except sqlite3.Error as e:
        print("An error occurred while fetching min and max years:", e)
        return 0


def get_min_max_power_to_weight_ratio(min_max_flag, database_path, table_name):
    min_max_column = "engine_hp / NULLIF(curb_weight_kg, 0)"  # Calculate power-to-weight ratio
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = f"SELECT MIN({min_max_column}) FROM {table_name}"
            elif min_max_flag == "max":
                search_query = f"SELECT MAX({min_max_column}) FROM {table_name}"
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                return round(result[0], 2)
    except sqlite3.Error as e:
        print(f"An error occurred while fetching {min_max_flag} power-to-weight ratio:", e)
        return None


def get_min_max_displacement(min_max_flag, database_path, table_names):
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = (f"SELECT MIN(capacity_cm3) FROM {table_names}")
            elif min_max_flag == "max":
                search_query = (f"SELECT MAX(capacity_cm3) FROM {table_names}")
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                return result[0]
    except sqlite3.Error as e:
        print("An error occurred while fetching min and max years:", e)
        return 0


def get_min_max_top_speed(min_max_flag, database_path, table_names):
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            if min_max_flag == "min":
                search_query = (f"SELECT MIN(CAST(max_speed_km_per_h AS REAL)) FROM {table_names} WHERE "
                                f"max_speed_km_per_h NOT LIKE '%[^0-9.]%'")
            elif min_max_flag == "max":
                search_query = (f"SELECT MAX(CAST(max_speed_km_per_h AS REAL)) FROM {table_names} WHERE "
                                f"max_speed_km_per_h NOT LIKE '%[^0-9.]%'")
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                return result[0]
    except sqlite3.Error as e:
        print("An error occurred while fetching min top speed:", e)
        return 0  # Return default value in case of an error


class CarSortGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Sorting")

        # Initialize fuel type vars
        self.fuel_type_gasoline_var = tkinter.IntVar(value=1)
        self.fuel_type_diesel_var = tkinter.IntVar(value=1)
        self.fuel_type_electric_var = tkinter.IntVar(value=1)
        self.fuel_type_hybrid_var = tkinter.IntVar(value=1)
        self.fuel_type_other_var = tkinter.IntVar(value=1)
        # Initialize engine placement vars
        self.engine_placement_front_var = tkinter.IntVar(value=1)
        self.engine_placement_mid_var = tkinter.IntVar(value=1)
        self.engine_placement_rear_var = tkinter.IntVar(value=1)
        # Initialize driven wheels vars
        self.drivetrain_fwd_var = tkinter.IntVar(value=1)
        self.drivetrain_rwd_var = tkinter.IntVar(value=1)
        self.drivetrain_awd_var = tkinter.IntVar(value=1)
        # Initialize car body type vars
        self.car_type_cabriolet_var = tkinter.IntVar(value=1)
        self.car_type_roadster_var = tkinter.IntVar(value=1)
        self.car_type_coupe_var = tkinter.IntVar(value=1)
        self.car_type_van_var = tkinter.IntVar(value=1)
        self.car_type_pickup_var = tkinter.IntVar(value=1)
        self.car_type_spyder_var = tkinter.IntVar(value=1)
        self.car_type_hatchback_var = tkinter.IntVar(value=1)
        self.car_type_sedan_var = tkinter.IntVar(value=1)
        self.car_type_limousine_var = tkinter.IntVar(value=1)
        self.car_type_wagon_var = tkinter.IntVar(value=1)
        self.car_type_suv_var = tkinter.IntVar(value=1)
        # Initialize transmission type vars
        self.transmission_manual_var = tkinter.IntVar(value=1)
        self.transmission_automatic_var = tkinter.IntVar(value=1)
        # Initialize bore:stroke ratio vars
        self.bore_stroke_ratio_undersquare_var = tkinter.IntVar(value=1)
        self.bore_stroke_ratio_square_var = tkinter.IntVar(value=1)
        self.bore_stroke_ratio_oversquare_var = tkinter.IntVar(value=1)

        self.country_selection = {}  # Dictionary to hold country selection states

        # Declaration of IntVar instances for each country
        self.United_Kingdom_var = tkinter.IntVar(value=1)
        self.Japan_var = tkinter.IntVar(value=1)
        self.Germany_var = tkinter.IntVar(value=1)
        self.Italy_var = tkinter.IntVar(value=1)
        self.France_var = tkinter.IntVar(value=1)
        self.United_States_var = tkinter.IntVar(value=1)
        self.Belgium_var = tkinter.IntVar(value=1)
        self.Romania_var = tkinter.IntVar(value=1)
        self.South_Korea_var = tkinter.IntVar(value=1)
        self.Russia_var = tkinter.IntVar(value=1)
        self.Switzerland_var = tkinter.IntVar(value=1)
        self.China_var = tkinter.IntVar(value=1)
        self.India_var = tkinter.IntVar(value=1)
        self.Latvia_var = tkinter.IntVar(value=1)
        self.Fictional_var = tkinter.IntVar(value=1)
        self.Malaysia_var = tkinter.IntVar(value=1)
        self.Netherlands_var = tkinter.IntVar(value=1)
        self.Poland_var = tkinter.IntVar(value=1)
        self.Czech_Republic_var = tkinter.IntVar(value=1)
        self.Spain_var = tkinter.IntVar(value=1)
        self.Australia_var = tkinter.IntVar(value=1)
        self.Iran_var = tkinter.IntVar(value=1)
        self.Sweden_var = tkinter.IntVar(value=1)
        self.Austria_var = tkinter.IntVar(value=1)
        self.Ukraine_var = tkinter.IntVar(value=1)
        self.Taiwan_var = tkinter.IntVar(value=1)
        self.Luxembourg_var = tkinter.IntVar(value=1)
        self.Brazil_var = tkinter.IntVar(value=1)
        self.Uzbekistan_var = tkinter.IntVar(value=1)
        self.Croatia_var = tkinter.IntVar(value=1)
        self.Turkey_var = tkinter.IntVar(value=1)
        self.Serbia_var = tkinter.IntVar(value=1)
        self.Kazakhstan_var = tkinter.IntVar(value=1)

        # Declaration of cylinder layouts (pistons and placements)
        self._8_var = tkinter.IntVar(value=1)
        self._4_var = tkinter.IntVar(value=1)
        self._6_var = tkinter.IntVar(value=1)
        self._5_var = tkinter.IntVar(value=1)
        self._2_var = tkinter.IntVar(value=1)
        self._12_var = tkinter.IntVar(value=1)
        self._3_var = tkinter.IntVar(value=1)
        self._10_var = tkinter.IntVar(value=1)
        self._1_var = tkinter.IntVar(value=1)
        self._7_var = tkinter.IntVar(value=1)
        self._16_var = tkinter.IntVar(value=1)
        self.V_type_var = tkinter.IntVar(value=1)
        self.Inline_var = tkinter.IntVar(value=1)
        self.Opposed_var = tkinter.IntVar(value=1)
        self.W_type_var = tkinter.IntVar(value=1)
        self.Rotary_var = tkinter.IntVar(value=1)

        # Create and configure widgets
        self.create_main_page()
        self.create_advanced_page()

        # Initially, show the main page
        self.show_main_page()

    def create_main_page(self):

        if not is_valid_sqlite3_database(database_path):
            messagebox.showerror("Invalid Database", "The database is invalid or cannot be accessed.")

        # Main page widgets are defined here
        self.main_frame = ttk.Frame(self.root)

        self.main_label = ttk.Label(self.main_frame, text="Basic Search")

        self.min_year_label = ttk.Label(self.main_frame, text=f"Min Year: {get_min_max_year(database_path, table_names, 'min')}")
        self.min_year_slider = ttk.Scale(self.main_frame, from_=get_min_max_year(database_path, table_names, "min"), to=get_min_max_year(database_path, table_names, "max"), orient="horizontal", length=200, command=self.update_year_labels)

        self.max_year_label = ttk.Label(self.main_frame, text=f"Max Year: {get_min_max_year(database_path, table_names, 'max')}")
        self.max_year_slider = ttk.Scale(self.main_frame, from_=get_min_max_year(database_path, table_names, "min"), to=get_min_max_year(database_path, table_names, "max"), orient="horizontal", length=200, command=self.update_year_labels)

        self.min_year_slider.set(get_min_max_year(database_path, table_names, "min"))
        self.max_year_slider.set(get_min_max_year(database_path, table_names, "max"))

        self.brand_label = ttk.Label(self.main_frame, text="Brand:")
        self.brand_dropdown = ttk.Combobox(self.main_frame, values=print_brand_names_only(database_path, table_names), height=20)
        # This code makes it so that if the user types or selects the Brand drop-down box, the model dropdown gets automatically updated
        #   to include the models offered by said brands
        self.brand_dropdown.bind("<<ComboboxSelected>>", self.update_model_dropdown)
        self.brand_dropdown.bind("<KeyRelease>", self.update_model_dropdown)

        # The model dropdown box is initialized as empty, its contents are decided by what brand is chosen by the user
        self.model_label = ttk.Label(self.main_frame, text="Model:")
        self.model_dropdown = ttk.Combobox(self.main_frame, values=[], height=20)

        self.results_label = ttk.Label(self.main_frame, text="Results:")
        self.results_text = tkinter.Text(self.main_frame, height=20, width=60)

        # The "command" value allows the programmer to establish a method to be executed when a button is clicked
        self.find_image_button = ttk.Button(self.main_frame, text="Find Image", command=lambda: self.on_find_image_button_click('basic'))

        self.go_to_website = ttk.Button(self.main_frame, text="Go to Website", command=lambda: self.go_to_make_website('basic'))

        self.search_button = ttk.Button(self.main_frame, text="Search")
        self.search_button["command"] = lambda: self.search_by_model(database_path, table_names, self.brand_dropdown.get(), self.model_dropdown.get(), round(self.min_year_slider.get()), round(self.max_year_slider.get()), variable_names, "simple")

        # Add the "See Advanced" button
        self.see_advanced_button = ttk.Button(self.main_frame, text="See Advanced", command=self.show_advanced_page)

        # Layout
        self.main_label.grid()
        self.min_year_label.grid()
        self.min_year_slider.grid()
        self.max_year_label.grid()
        self.max_year_slider.grid()
        self.brand_label.grid()
        self.brand_dropdown.grid()
        self.model_label.grid()
        self.model_dropdown.grid()
        self.results_label.grid()
        self.results_text.grid()
        self.find_image_button.grid()
        self.go_to_website.grid()
        self.search_button.grid()
        # self.search_date_only_button.grid()
        self.see_advanced_button.grid()

    # noinspection PyTypeChecker
    def search_by_model(self, database_path, table_names, brand, model, year_from, year_to, variable_names, complexity):
        results, count, *_ = search_by_model(database_path, table_names, brand, model, year_from, year_to, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, variable_names, complexity, None, None, None, None)

        if results and results != "T" and count != 'h':
            # Clear the existing text in the Text widget
            self.results_text.delete(1.0, tkinter.END)
            # Insert the results into the Text widget
            self.results_text.insert(tkinter.END, results)
            self.results_label.config(text=f"Results: {count}")
        else:
            # If no results were found, show a message
            self.results_text.delete(1.0, tkinter.END)
            self.results_text.insert(tkinter.END, "No data found for this search, OR, an error occured")

    # This method calls the search_by_model method and formats the data appropriately, updating the correct GUI elements to allow the data to be displayed to the user
    def search_by_model_advanced_page(self, database_path, table_names, brand, model, year_from, year_to, seating_capacity_min, seating_capacity_max, engine_hp_min, engine_hp_max, curb_weight_kg_min, curb_weight_kg_max, power_to_weight_ratio_min, power_to_weight_ratio_max, displacement_min, displacement_max, top_speed_min, top_speed_max, engine_front_bool, engine_mid_bool, engine_rear_bool, gasoline_bool, diesel_bool, hybrid_bool, electric_bool, other_fuel_type_bool, fwd_drivetrain_bool, rwd_drivetrain_bool, awd_drivetrain_bool, car_type_roadster_bool, car_type_coupe_bool, car_type_hatchback_bool, car_type_spyder_bool, car_type_cabriolet_bool, car_type_sedan_bool, car_type_wagon_bool, car_type_suv_bool, car_type_pickup_bool, car_type_van_bool, car_type_limousine_bool, manual_transmission_bool, automatic_transmission_bool, Bore_Stroke_Undersquare_bool, Bore_Stroke_Square_bool, Bore_Stroke_Oversquare_bool, United_Kingdom_bool, Japan_bool, Germany_bool, Italy_bool, France_bool, United_States_bool, Belgium_bool, Romania_bool, South_Korea_bool, Russia_bool, Switzerland_bool, China_bool, India_bool, Latvia_bool, Fictional_bool, Malaysia_bool, Netherlands_bool, Poland_bool, Czech_Republic_bool, Spain_bool, Australia_bool, Iran_bool, Sweden_bool, Austria_bool, Ukraine_bool, Taiwan_bool, Luxembourg_bool, Brazil_bool, Uzbekistan_bool, Croatia_bool, Turkey_bool, Serbia_bool, Kazakhstan_bool, _8_cylinders_bool, _4_cylinders_bool, _6_cylinders_bool, _5_cylinders_bool, _2_cylinders_bool, _12_cylinders_bool, _3_cylinders_bool, _10_cylinders_bool, _1_cylinders_bool, _7_cylinders_bool, _16_cylinders_bool, V_type_engine_layout_bool, Inline_engine_layout_bool, Opposed_engine_layout_bool, W_type_engine_layout_bool, Rotary_engine_layout_bool, variable_names, complexity, csv_export_boolean, query_export_boolean, query_import_boolean, query):
        results, count, *_ = search_by_model(database_path, table_names, brand, model, year_from, year_to, seating_capacity_min, seating_capacity_max, engine_hp_min, engine_hp_max, curb_weight_kg_min, curb_weight_kg_max, power_to_weight_ratio_min, power_to_weight_ratio_max, displacement_min, displacement_max, top_speed_min, top_speed_max, engine_front_bool, engine_mid_bool, engine_rear_bool, gasoline_bool, diesel_bool, hybrid_bool, electric_bool, other_fuel_type_bool, fwd_drivetrain_bool, rwd_drivetrain_bool, awd_drivetrain_bool, car_type_roadster_bool, car_type_coupe_bool, car_type_hatchback_bool, car_type_spyder_bool, car_type_cabriolet_bool, car_type_sedan_bool, car_type_wagon_bool, car_type_suv_bool, car_type_pickup_bool, car_type_van_bool, car_type_limousine_bool, manual_transmission_bool, automatic_transmission_bool, Bore_Stroke_Undersquare_bool, Bore_Stroke_Square_bool, Bore_Stroke_Oversquare_bool, United_Kingdom_bool, Japan_bool, Germany_bool, Italy_bool, France_bool, United_States_bool, Belgium_bool, Romania_bool, South_Korea_bool, Russia_bool, Switzerland_bool, China_bool, India_bool, Latvia_bool, Fictional_bool, Malaysia_bool, Netherlands_bool, Poland_bool, Czech_Republic_bool, Spain_bool, Australia_bool, Iran_bool, Sweden_bool, Austria_bool, Ukraine_bool, Taiwan_bool, Luxembourg_bool, Brazil_bool, Uzbekistan_bool, Croatia_bool, Turkey_bool, Serbia_bool, Kazakhstan_bool, _8_cylinders_bool, _4_cylinders_bool, _6_cylinders_bool, _5_cylinders_bool, _2_cylinders_bool, _12_cylinders_bool, _3_cylinders_bool, _10_cylinders_bool, _1_cylinders_bool, _7_cylinders_bool, _16_cylinders_bool, V_type_engine_layout_bool, Inline_engine_layout_bool, Opposed_engine_layout_bool, W_type_engine_layout_bool, Rotary_engine_layout_bool, variable_names, complexity, csv_export_boolean, query_export_boolean, query_import_boolean, query)

        if results and results != "T" and count != 'h':
            # Clear the existing text in the Text widget
            self.results_text2.delete(1.0, tkinter.END)
            # Insert the results into the Text widget
            self.results_text2.insert(tkinter.END, results)
            self.results_label2.config(text=f"Results: {count}")
        else:
            # If no results were found, show a message
            self.results_text2.delete(1.0, tkinter.END)
            self.results_text2.insert(tkinter.END, "No data found for this search, OR, an error occured")
            self.results_label2.config(text=f"Results:")

    # This method updates the model dropdown based on what brand is chosen, using the search_by_brand_show_model_only method
    def update_model_dropdown(self, event):
        selected_brand = self.brand_dropdown.get()
        if selected_brand.strip() != '':
            models = search_by_brand_show_model_only(database_path, table_names, selected_brand)
            self.model_dropdown['values'] = models
        else:
            self.model_dropdown['values'] = None
            self.model_dropdown.set("")

    # Method to update year labels
    def update_year_labels(self, event):
        self.min_year_label["text"] = f"Min Year: {round(self.min_year_slider.get())}"
        self.max_year_label["text"] = f"Max Year: {round(self.max_year_slider.get())}"

    # Method to update year labels on the advanced page
    def update_year_labels_advanced_page(self, event):
        self.min_year_label2["text"] = f"Min Year: {round(self.min_year_slider2.get())}"
        self.max_year_label2["text"] = f"Max Year: {round(self.max_year_slider2.get())}"

    # Method to update seats labels
    def update_seats_label_advanced_page(self, event):
        self.min_seating_capacity_label[
            "text"] = f"Min Seating Capacity: {round(self.min_seating_capacity_slider.get())}"
        self.max_seating_capacity_label[
            "text"] = f"Max Seating Capacity: {round(self.max_seating_capacity_slider.get())}"

    # Method to update horsepower labels on the advanced page
    def update_engine_hp_label_advanced_page(self, event):
        self.min_horsepower_label["text"] = f"Min Horsepower: {round(self.min_horsepower_slider.get())}"
        self.max_horsepower_label["text"] = f"Max Horsepower: {round(self.max_horsepower_slider.get())}"

    # Method to update curb weight labels on the advanced page
    def update_curb_weight_kg_advanced_page(self, event):
        self.min_weight_label["text"] = f"Min Weight (Kg): {round(self.min_weight_slider.get())}"
        self.max_weight_label["text"] = f"Max Weight (Kg): {round(self.max_weight_slider.get())}"

    # Method to update power:weight ratio labels on the advanced page
    def update_powertoweight_advanced_page(self, event):
        self.min_powertoweight_label["text"] = f"Min HP / Weight Ratio: {round(self.min_powertoweight_slider.get(), 2)}"
        self.max_powertoweight_label["text"] = f"Max HP / Weight Ratio: {round(self.max_powertoweight_slider.get(), 2)}"

    # Method to update displacement labels on the advanced page
    def update_displacement_advanced_page(self, event):
        self.min_displacement_label["text"] = f"Min Displacement (cm3): {round(self.min_displacement_slider.get())}"
        self.max_displacement_label["text"] = f"Max Displacement (cm3): {round(self.max_displacement_slider.get())}"

    # Method to update top speed labels on the advanced page
    def update_top_speed_advanced_page(self, event):
        self.min_top_speed_label["text"] = f"Min Top Speed (Km/h): {round(self.min_top_speed_slider.get())}"
        self.max_top_speed_label["text"] = f"Max Top Speed (Km/h): {round(self.max_top_speed_slider.get())}"

    # Method to update all the labels on the advanced page
    #   This method is only called at the creation of the advanced page
    def update_all_sliders_advanced_page(self, event):
        self.min_powertoweight_label["text"] = f"Min HP / Weight Ratio: {round(self.min_powertoweight_slider.get(), 2)}"
        self.max_powertoweight_label["text"] = f"Max HP / Weight Ratio: {round(self.max_powertoweight_slider.get(), 2)}"
        selected_brand = self.brand_dropdown.get()
        models = search_by_brand_show_model_only(database_path, table_names, selected_brand)
        self.model_dropdown['values'] = models
        self.min_year_label["text"] = f"Min Year: {round(self.min_year_slider.get())}"
        self.max_year_label["text"] = f"Max Year: {round(self.max_year_slider.get())}"
        self.min_year_label2["text"] = f"Min Year: {round(self.min_year_slider2.get())}"
        self.max_year_label2["text"] = f"Max Year: {round(self.max_year_slider2.get())}"
        self.min_seating_capacity_label["text"] = f"Min Seating Capacity: {round(self.min_seating_capacity_slider.get())}"
        self.max_seating_capacity_label["text"] = f"Max Seating Capacity: {round(self.max_seating_capacity_slider.get())}"
        self.min_horsepower_label["text"] = f"Min Horsepower: {round(self.min_horsepower_slider.get())}"
        self.max_horsepower_label["text"] = f"Max Horsepower: {round(self.max_horsepower_slider.get())}"
        self.min_weight_label["text"] = f"Min Weight (Kg): {round(self.min_weight_slider.get())}"
        self.max_weight_label["text"] = f"Max Weight (Kg): {round(self.max_weight_slider.get())}"
        self.min_displacement_label["text"] = f"Min Displacement (cm3): {round(self.min_displacement_slider.get())}"
        self.max_displacement_label["text"] = f"Max Displacement (cm3): {round(self.max_displacement_slider.get())}"

    # Method to reset all the paramaters on the advanced page to their default values
    def reset_all_paramaters_advanced_page(self):

        variables_to_reset = [
            self.fuel_type_gasoline_var, self.fuel_type_diesel_var, self.fuel_type_electric_var,
            self.fuel_type_hybrid_var, self.fuel_type_other_var, self.engine_placement_front_var,
            self.engine_placement_mid_var, self.engine_placement_rear_var, self.drivetrain_fwd_var,
            self.drivetrain_rwd_var, self.drivetrain_awd_var, self.car_type_cabriolet_var,
            self.car_type_roadster_var, self.car_type_coupe_var, self.car_type_van_var,
            self.car_type_pickup_var, self.car_type_spyder_var, self.car_type_hatchback_var,
            self.car_type_sedan_var, self.car_type_wagon_var, self.car_type_limousine_var,
            self.car_type_suv_var, self.brand_dropdown2, self.model_dropdown2,
            self.min_year_slider2, self.max_year_slider2, self.min_seating_capacity_slider,
            self.max_seating_capacity_slider, self.min_weight_slider, self.max_weight_slider,
            self.min_horsepower_slider, self.max_horsepower_slider, self.min_powertoweight_slider,
            self.max_powertoweight_slider, self.min_displacement_slider, self.max_displacement_slider,
            self.min_top_speed_slider, self.max_top_speed_slider, self.transmission_automatic_var,
            self.transmission_manual_var, self.bore_stroke_ratio_undersquare_var,
            self.bore_stroke_ratio_square_var, self.bore_stroke_ratio_oversquare_var,
            self.United_Kingdom_var, self.Japan_var, self.Germany_var, self.Italy_var,
            self.France_var, self.United_States_var, self.Belgium_var, self.Romania_var,
            self.South_Korea_var, self.Russia_var, self.Switzerland_var, self.China_var,
            self.India_var, self.Latvia_var, self.Fictional_var, self.Malaysia_var,
            self.Netherlands_var, self.Poland_var, self.Czech_Republic_var, self.Spain_var,
            self.Australia_var, self.Iran_var, self.Sweden_var, self.Austria_var,
            self.Ukraine_var, self.Taiwan_var, self.Luxembourg_var, self.Brazil_var,
            self.Uzbekistan_var, self.Croatia_var, self.Turkey_var, self.Serbia_var,
            self.Kazakhstan_var, self._8_var, self._4_var, self._6_var, self._5_var,
            self._2_var, self._12_var, self._3_var, self._10_var, self._1_var,
            self._7_var, self._16_var, self.V_type_var, self.Inline_var, self.Opposed_var,
            self.W_type_var, self.Rotary_var
            ]

        for var in variables_to_reset:
            var.set(1)

        self.brand_dropdown2.set("")
        self.model_dropdown2.set("")
        self.min_year_slider2.set(get_min_max_year(database_path, table_names, "min"))
        self.max_year_slider2.set(get_min_max_year(database_path, table_names, "max"))
        self.min_seating_capacity_slider.set(get_min_max_seating_capacity("min", database_path, table_names))
        self.max_seating_capacity_slider.set(get_min_max_seating_capacity("max", database_path, table_names))
        self.min_weight_slider.set(get_min_max_curb_weight('min', database_path, table_names))
        self.max_weight_slider.set(get_min_max_curb_weight('max', database_path, table_names))
        self.min_horsepower_slider.set(get_min_max_engine_hp('min', database_path, table_names))
        self.max_horsepower_slider.set(get_min_max_engine_hp('max', database_path, table_names))
        self.min_powertoweight_slider.set(get_min_max_power_to_weight_ratio('min', database_path, table_names))
        self.max_powertoweight_slider.set(get_min_max_power_to_weight_ratio('max', database_path, table_names))
        self.min_displacement_slider.set(get_min_max_displacement('min', database_path, table_names))
        self.max_displacement_slider.set(get_min_max_displacement('max', database_path, table_names))
        self.min_top_speed_slider.set(get_min_max_top_speed('min', database_path, table_names))
        self.max_top_speed_slider.set(get_min_max_top_speed('max', database_path, table_names))

        # update after resetting
        self.update_all_sliders_advanced_page(self)

    # Method that sets all checkboxes to 0, "clearing" them
    def clear_all_checkboxes(self):

        checkboxes_to_clear = [
            self.fuel_type_gasoline_var, self.fuel_type_diesel_var, self.fuel_type_electric_var,
            self.fuel_type_hybrid_var, self.fuel_type_other_var, self.engine_placement_front_var,
            self.engine_placement_mid_var, self.engine_placement_rear_var, self.drivetrain_fwd_var,
            self.drivetrain_rwd_var, self.drivetrain_awd_var, self.car_type_cabriolet_var,
            self.car_type_roadster_var, self.car_type_coupe_var, self.car_type_van_var,
            self.car_type_pickup_var, self.car_type_spyder_var, self.car_type_hatchback_var,
            self.car_type_sedan_var, self.car_type_wagon_var, self.car_type_limousine_var,
            self.car_type_suv_var, self.transmission_automatic_var, self.transmission_manual_var,
            self.bore_stroke_ratio_undersquare_var, self.bore_stroke_ratio_square_var,
            self.bore_stroke_ratio_oversquare_var, self.United_Kingdom_var, self.Japan_var,
            self.Germany_var, self.Italy_var, self.France_var, self.United_States_var,
            self.Belgium_var, self.Romania_var, self.South_Korea_var, self.Russia_var,
            self.Switzerland_var, self.China_var, self.India_var, self.Latvia_var,
            self.Fictional_var, self.Malaysia_var, self.Netherlands_var, self.Poland_var,
            self.Czech_Republic_var, self.Spain_var, self.Australia_var, self.Iran_var,
            self.Sweden_var, self.Austria_var, self.Ukraine_var, self.Taiwan_var,
            self.Luxembourg_var, self.Brazil_var, self.Uzbekistan_var, self.Croatia_var,
            self.Turkey_var, self.Serbia_var, self.Kazakhstan_var, self._8_var, self._4_var,
            self._6_var, self._5_var, self._2_var, self._12_var, self._3_var, self._10_var,
            self._1_var, self._7_var, self._16_var, self.V_type_var, self.Inline_var,
            self.Opposed_var, self.W_type_var, self.Rotary_var
            ]

        # Clear all checkboxes
        for checkbox in checkboxes_to_clear:
            checkbox.set(0)

    def create_advanced_page(self):

        # Method that allows the user to import an SQL query, which then is directly executed
        def execute_sql_query():
            query = self.sql_query_textbox.get("1.0", tkinter.END)
            self.search_by_model_advanced_page(database_path, table_names, self.brand_dropdown2.get(), self.model_dropdown2.get(), round(self.min_year_slider2.get()), round(self.max_year_slider2.get()), round(self.min_seating_capacity_slider.get()), round(self.max_seating_capacity_slider.get()),
                round(self.min_horsepower_slider.get()), round(self.max_horsepower_slider.get()), round(self.min_weight_slider.get()), round(self.max_weight_slider.get()), round(self.min_powertoweight_slider.get(), 2), round(self.max_powertoweight_slider.get(), 2), round(self.min_displacement_slider.get()),
                round(self.max_displacement_slider.get()), round(self.min_top_speed_slider.get()), round(self.max_top_speed_slider.get()), self.engine_placement_front_var.get(), self.engine_placement_mid_var.get(), self.engine_placement_rear_var.get(), self.fuel_type_gasoline_var.get(),
                self.fuel_type_diesel_var.get(), self.fuel_type_hybrid_var.get(), self.fuel_type_electric_var.get(), self.fuel_type_other_var.get(), self.drivetrain_fwd_var.get(), self.drivetrain_rwd_var.get(), self.drivetrain_awd_var.get(), self.car_type_roadster_var.get(), self.car_type_coupe_var.get(),
                self.car_type_hatchback_var.get(), self.car_type_spyder_var.get(), self.car_type_cabriolet_var.get(), self.car_type_sedan_var.get(), self.car_type_wagon_var.get(), self.car_type_suv_var.get(), self.car_type_pickup_var.get(), self.car_type_van_var.get(), self.car_type_limousine_var.get(),
                self.transmission_manual_var.get(), self.transmission_automatic_var.get(), self.bore_stroke_ratio_undersquare_var.get(), self.bore_stroke_ratio_square_var.get(), self.bore_stroke_ratio_oversquare_var.get(), self.United_Kingdom_var.get(), self.Japan_var.get(), self.Germany_var.get(),
                self.Italy_var.get(), self.France_var.get(), self.United_States_var.get(), self.Belgium_var.get(), self.Romania_var.get(), self.South_Korea_var.get(), self.Russia_var.get(), self.Switzerland_var.get(), self.China_var.get(), self.India_var.get(), self.Latvia_var.get(), self.Fictional_var.get(),
                self.Malaysia_var.get(), self.Netherlands_var.get(), self.Poland_var.get(), self.Czech_Republic_var.get(), self.Spain_var.get(), self.Australia_var.get(), self.Iran_var.get(), self.Sweden_var.get(), self.Austria_var.get(), self.Ukraine_var.get(), self.Taiwan_var.get(), self.Luxembourg_var.get(),
                self.Brazil_var.get(), self.Uzbekistan_var.get(), self.Croatia_var.get(), self.Turkey_var.get(), self.Serbia_var.get(), self.Kazakhstan_var.get(), self._8_var.get(), self._4_var.get(), self._6_var.get(), self._5_var.get(), self._2_var.get(), self._12_var.get(), self._3_var.get(), self._10_var.get(),
                self._1_var.get(), self._7_var.get(), self._16_var.get(), self.V_type_var.get(), self.Inline_var.get(), self.Opposed_var.get(), self.W_type_var.get(), self.Rotary_var.get(), variable_names, "advanced", 0, 0, 1, query)

        # Clears the SQL Query dialogue box
        def clear_text():
            # Clear the SQL query textbox and result textbox
            self.sql_query_textbox.delete("1.0", tkinter.END)

        # Advanced page widgets are initialized here
        self.advanced_frame = ttk.Frame(self.root)

        self.advanced_label = ttk.Label(self.advanced_frame, text="Advanced Search")
        self.return_button = ttk.Button(self.advanced_frame, text="Return to Basic Search", command=self.show_main_page)

        self.brand_label2 = ttk.Label(self.advanced_frame, text="Brand:")
        self.brand_dropdown2 = ttk.Combobox(self.advanced_frame, values=print_brand_names_only(database_path, table_names))
        self.brand_dropdown2.bind("<<ComboboxSelected>>", self.update_model_dropdown2)
        self.brand_dropdown2.bind("<KeyRelease>", self.update_model_dropdown2)

        self.model_label2 = ttk.Label(self.advanced_frame, text="Model:")
        self.model_dropdown2 = ttk.Combobox(self.advanced_frame, values=[])
        # self.model_dropdown2.bind("<KeyRelease>", self.update_model_dropdown)

        # Add detailed search elements (sliders, checkboxes, etc.)
        self.min_year_label2 = ttk.Label(self.advanced_frame, text=f"Min Year: {get_min_max_year(database_path, table_names, 'min')}")
        self.min_year_slider2 = ttk.Scale(self.advanced_frame, from_=get_min_max_year(database_path, table_names, 'min'), to=get_min_max_year(database_path, table_names, "max"), orient="horizontal", length=200, command=self.update_year_labels_advanced_page)
        self.max_year_label2 = ttk.Label(self.advanced_frame, text=f"Max Year: {get_min_max_year(database_path, table_names, 'max')}")
        self.max_year_slider2 = ttk.Scale(self.advanced_frame, from_=get_min_max_year(database_path, table_names, 'min'), to=get_min_max_year(database_path, table_names, "max"), orient="horizontal", length=200, command=self.update_year_labels_advanced_page)

        self.min_seating_capacity_label = ttk.Label(self.advanced_frame, text=f"Min Seating Capacity: {get_min_max_seating_capacity('min', database_path, table_names)}")
        self.min_seating_capacity_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_seating_capacity("min", database_path, table_names), to=get_min_max_seating_capacity("max", database_path, table_names), orient="horizontal", length=200, command=self.update_seats_label_advanced_page)
        self.max_seating_capacity_label = ttk.Label(self.advanced_frame, text=f"Max Seating Capacity: {get_min_max_seating_capacity('max', database_path, table_names)}")
        self.max_seating_capacity_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_seating_capacity("min", database_path, table_names), to=get_min_max_seating_capacity("max", database_path, table_names), orient="horizontal", length=200, command=self.update_seats_label_advanced_page)
        self.min_seating_capacity_slider.set(get_min_max_seating_capacity("min", database_path, table_names))

        self.min_horsepower_label = ttk.Label(self.advanced_frame, text=f"Min Horsepower: {get_min_max_engine_hp('min', database_path, table_names)}")
        self.min_horsepower_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_engine_hp("min", database_path, table_names), to=get_min_max_engine_hp("max", database_path, table_names), orient="horizontal", length=200, command=self.update_engine_hp_label_advanced_page)
        self.max_horsepower_label = ttk.Label(self.advanced_frame, text=f"Max Horsepower: {get_min_max_engine_hp('max', database_path, table_names)}")
        self.max_horsepower_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_engine_hp("min", database_path, table_names), to=get_min_max_engine_hp("max", database_path, table_names), orient="horizontal", length=200, command=self.update_engine_hp_label_advanced_page)

        self.min_weight_label = ttk.Label(self.advanced_frame, text=f"Min Weight: {get_min_max_curb_weight('min', database_path, table_names)}")
        self.min_weight_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_curb_weight('min', database_path, table_names), to=get_min_max_curb_weight('max', database_path, table_names), orient="horizontal", length=200, command=self.update_curb_weight_kg_advanced_page)
        self.max_weight_label = ttk.Label(self.advanced_frame, text=f"Max Weight: {get_min_max_curb_weight('max', database_path, table_names)}")
        self.max_weight_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_curb_weight('min', database_path, table_names), to=get_min_max_curb_weight('max', database_path, table_names), orient="horizontal", length=200, command=self.update_curb_weight_kg_advanced_page)

        self.min_powertoweight_label = ttk.Label(self.advanced_frame, text=f"Min HP / Weight Ratio: {get_min_max_power_to_weight_ratio('min', database_path, table_names)}")
        self.min_powertoweight_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_power_to_weight_ratio('min', database_path, table_names), to=get_min_max_power_to_weight_ratio("max", database_path, table_names), orient="horizontal", length=200, command=self.update_powertoweight_advanced_page)
        self.max_powertoweight_label = ttk.Label(self.advanced_frame, text=f"Max HP / Weight Ratio: {get_min_max_power_to_weight_ratio('max', database_path, table_names)}")
        self.max_powertoweight_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_power_to_weight_ratio('min', database_path, table_names), to=get_min_max_power_to_weight_ratio("max", database_path, table_names), orient="horizontal", length=200, command=self.update_powertoweight_advanced_page)

        self.min_displacement_label = ttk.Label(self.advanced_frame, text=f"Min Displacement cm3: {get_min_max_displacement('min', database_path, table_names)}")
        self.min_displacement_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_displacement('min', database_path, table_names), to=get_min_max_displacement('max', database_path, table_names), orient="horizontal", length=200, command=self.update_displacement_advanced_page)
        self.max_displacement_label = ttk.Label(self.advanced_frame, text=f"Max Displacement cm3: {get_min_max_displacement('max', database_path, table_names)}")
        self.max_displacement_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_displacement('min', database_path, table_names), to=get_min_max_displacement('max', database_path, table_names), orient="horizontal", length=200, command=self.update_displacement_advanced_page)

        self.min_top_speed_label = ttk.Label(self.advanced_frame, text=f"Min Top Speed (Km/h): {get_min_max_top_speed('min', database_path, table_names)}")
        self.min_top_speed_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_top_speed('min', database_path, table_names), to=get_min_max_top_speed('max', database_path, table_names), orient="horizontal", length=200, command=self.update_top_speed_advanced_page)
        self.max_top_speed_label = ttk.Label(self.advanced_frame, text=f"Max Top Speed (Km/h): {get_min_max_top_speed('max', database_path, table_names)}")
        self.max_top_speed_slider = ttk.Scale(self.advanced_frame, from_=get_min_max_top_speed('min', database_path, table_names), to=get_min_max_top_speed('max', database_path, table_names), orient="horizontal", length=200, command=self.update_top_speed_advanced_page)

        # Add checkboxes
        self.engine_placement_label = ttk.Label(self.advanced_frame, text="Engine Placement:")
        self.engine_placement_front = ttk.Checkbutton(self.advanced_frame, text="Front", variable=self.engine_placement_front_var)
        self.engine_placement_mid = ttk.Checkbutton(self.advanced_frame, text="Mid", variable=self.engine_placement_mid_var)
        self.engine_placement_rear = ttk.Checkbutton(self.advanced_frame, text="Rear", variable=self.engine_placement_rear_var)

        self.fuel_type_label = ttk.Label(self.advanced_frame, text="Engine Type:")
        self.fuel_type_gasoline = ttk.Checkbutton(self.advanced_frame, text="Gasoline", variable=self.fuel_type_gasoline_var)
        self.fuel_type_diesel = ttk.Checkbutton(self.advanced_frame, text="Diesel", variable=self.fuel_type_diesel_var)
        self.fuel_type_electric = ttk.Checkbutton(self.advanced_frame, text="Electric", variable=self.fuel_type_electric_var)
        self.fuel_type_hybrid = ttk.Checkbutton(self.advanced_frame, text="Hybrid", variable=self.fuel_type_hybrid_var)
        self.fuel_type_other = ttk.Checkbutton(self.advanced_frame, text="Other", variable=self.fuel_type_other_var)

        self.fuel_type_gasoline.setvar()

        self.body_type_label = ttk.Label(self.advanced_frame, text="Body Type:")
        self.body_type_options = ["Roadster", "Coupe", "Hatchback", "Spyder", "Cabriolet", "Sedan", "Wagon", "SUV",
                                  "Pickup", "Van", "Limousine"]
        self.body_type_vars = [self.car_type_roadster_var, self.car_type_coupe_var, self.car_type_hatchback_var,
                               self.car_type_spyder_var, self.car_type_cabriolet_var, self.car_type_sedan_var,
                               self.car_type_wagon_var, self.car_type_suv_var, self.car_type_pickup_var,
                               self.car_type_van_var, self.car_type_limousine_var]
        self.body_type_checkboxes = [ttk.Checkbutton(self.advanced_frame, text=option, variable=var) for option, var in zip(self.body_type_options, self.body_type_vars)]

        self.drivetrain_label = ttk.Label(self.advanced_frame, text="Drivetrain:")
        self.drivetrain_rwd = ttk.Checkbutton(self.advanced_frame, text="RWD", variable=self.drivetrain_rwd_var)
        self.drivetrain_fwd = ttk.Checkbutton(self.advanced_frame, text="FWD", variable=self.drivetrain_fwd_var)
        self.drivetrain_awd = ttk.Checkbutton(self.advanced_frame, text="AWD", variable=self.drivetrain_awd_var)

        self.transmission_label = ttk.Label(self.advanced_frame, text="Transmission:")
        self.transmission_manual = ttk.Checkbutton(self.advanced_frame, text="Manual", variable=self.transmission_manual_var)
        self.transmission_automatic = ttk.Checkbutton(self.advanced_frame, text="Automatic", variable=self.transmission_automatic_var)

        self.bore_stroke_ratio_label = ttk.Label(self.advanced_frame, text="Bore/Stroke Ratio:")
        self.bore_stroke_ratio_undersquare = ttk.Checkbutton(self.advanced_frame, text="Undersquare", variable=self.bore_stroke_ratio_undersquare_var)
        self.bore_stroke_ratio_square = ttk.Checkbutton(self.advanced_frame, text="Square", variable=self.bore_stroke_ratio_square_var)
        self.bore_stroke_ratio_oversquare = ttk.Checkbutton(self.advanced_frame, text="Overquare", variable=self.bore_stroke_ratio_oversquare_var)

        self.open_countries_page_button = ttk.Button(self.advanced_frame, text="Countries of Origin:", command=self.create_country_of_origin_page)

        self.open_engine_layout_page_button = ttk.Button(self.advanced_frame, text="Engine Layouts:", command=self.create_engine_layout_selector_page)

        self.find_image_button = ttk.Button(self.advanced_frame, text="Find Image", command=lambda: self.on_find_image_button_click('advanced'))

        self.go_to_website = ttk.Button(self.advanced_frame, text="Go to Website", command=lambda: self.go_to_make_website('advanced'))

        self.export_to_CSV_button = ttk.Button(self.advanced_frame, text="Export to CSV")
        self.export_to_CSV_button["command"] = lambda: self.search_by_model_advanced_page(database_path, table_names, self.brand_dropdown2.get(), self.model_dropdown2.get(), round(self.min_year_slider2.get()), round(self.max_year_slider2.get()), round(self.min_seating_capacity_slider.get()), round(self.max_seating_capacity_slider.get()), round(self.min_horsepower_slider.get()), round(self.max_horsepower_slider.get()), round(self.min_weight_slider.get()), round(self.max_weight_slider.get()), round(self.min_powertoweight_slider.get(), 2), round(self.max_powertoweight_slider.get(), 2), round(self.min_displacement_slider.get()), round(self.max_displacement_slider.get()), round(self.min_top_speed_slider.get()), round(self.max_top_speed_slider.get()), self.engine_placement_front_var.get(), self.engine_placement_mid_var.get(), self.engine_placement_rear_var.get(), self.fuel_type_gasoline_var.get(), self.fuel_type_diesel_var.get(), self.fuel_type_hybrid_var.get(), self.fuel_type_electric_var.get(), self.fuel_type_other_var.get(), self.drivetrain_fwd_var.get(), self.drivetrain_rwd_var.get(), self.drivetrain_awd_var.get(), self.car_type_roadster_var.get(), self.car_type_coupe_var.get(), self.car_type_hatchback_var.get(), self.car_type_spyder_var.get(), self.car_type_cabriolet_var.get(), self.car_type_sedan_var.get(), self.car_type_wagon_var.get(), self.car_type_suv_var.get(), self.car_type_pickup_var.get(), self.car_type_van_var.get(), self.car_type_limousine_var.get(), self.transmission_manual_var.get(), self.transmission_automatic_var.get(), self.bore_stroke_ratio_undersquare_var.get(), self.bore_stroke_ratio_square_var.get(), self.bore_stroke_ratio_oversquare_var.get(), self.United_Kingdom_var.get(), self.Japan_var.get(), self.Germany_var.get(), self.Italy_var.get(), self.France_var.get(), self.United_States_var.get(), self.Belgium_var.get(), self.Romania_var.get(), self.South_Korea_var.get(), self.Russia_var.get(), self.Switzerland_var.get(), self.China_var.get(), self.India_var.get(), self.Latvia_var.get(), self.Fictional_var.get(), self.Malaysia_var.get(), self.Netherlands_var.get(), self.Poland_var.get(), self.Czech_Republic_var.get(), self.Spain_var.get(), self.Australia_var.get(), self.Iran_var.get(), self.Sweden_var.get(), self.Austria_var.get(), self.Ukraine_var.get(), self.Taiwan_var.get(), self.Luxembourg_var.get(), self.Brazil_var.get(), self.Uzbekistan_var.get(), self.Croatia_var.get(), self.Turkey_var.get(), self.Serbia_var.get(), self.Kazakhstan_var.get(), self._8_var.get(), self._4_var.get(), self._6_var.get(), self._5_var.get(), self._2_var.get(), self._12_var.get(), self._3_var.get(), self._10_var.get(), self._1_var.get(), self._7_var.get(), self._16_var.get(), self.V_type_var.get(), self.Inline_var.get(), self.Opposed_var.get(), self.W_type_var.get(), self.Rotary_var.get(), variable_names, "advanced", 1, 0, 0, None)

        self.export_sql_query_button = ttk.Button(self.advanced_frame, text="Save Search")
        self.export_sql_query_button["command"] = lambda: self.search_by_model_advanced_page(database_path, table_names, self.brand_dropdown2.get(), self.model_dropdown2.get(), round(self.min_year_slider2.get()), round(self.max_year_slider2.get()), round(self.min_seating_capacity_slider.get()), round(self.max_seating_capacity_slider.get()), round(self.min_horsepower_slider.get()), round(self.max_horsepower_slider.get()), round(self.min_weight_slider.get()), round(self.max_weight_slider.get()), round(self.min_powertoweight_slider.get(), 2), round(self.max_powertoweight_slider.get(), 2), round(self.min_displacement_slider.get()), round(self.max_displacement_slider.get()), round(self.min_top_speed_slider.get()), round(self.max_top_speed_slider.get()), self.engine_placement_front_var.get(), self.engine_placement_mid_var.get(), self.engine_placement_rear_var.get(), self.fuel_type_gasoline_var.get(), self.fuel_type_diesel_var.get(), self.fuel_type_hybrid_var.get(), self.fuel_type_electric_var.get(), self.fuel_type_other_var.get(), self.drivetrain_fwd_var.get(), self.drivetrain_rwd_var.get(), self.drivetrain_awd_var.get(), self.car_type_roadster_var.get(), self.car_type_coupe_var.get(), self.car_type_hatchback_var.get(), self.car_type_spyder_var.get(), self.car_type_cabriolet_var.get(), self.car_type_sedan_var.get(), self.car_type_wagon_var.get(), self.car_type_suv_var.get(), self.car_type_pickup_var.get(), self.car_type_van_var.get(), self.car_type_limousine_var.get(), self.transmission_manual_var.get(), self.transmission_automatic_var.get(), self.bore_stroke_ratio_undersquare_var.get(), self.bore_stroke_ratio_square_var.get(), self.bore_stroke_ratio_oversquare_var.get(), self.United_Kingdom_var.get(), self.Japan_var.get(), self.Germany_var.get(), self.Italy_var.get(), self.France_var.get(), self.United_States_var.get(), self.Belgium_var.get(), self.Romania_var.get(), self.South_Korea_var.get(), self.Russia_var.get(), self.Switzerland_var.get(), self.China_var.get(), self.India_var.get(), self.Latvia_var.get(), self.Fictional_var.get(), self.Malaysia_var.get(), self.Netherlands_var.get(), self.Poland_var.get(), self.Czech_Republic_var.get(), self.Spain_var.get(), self.Australia_var.get(), self.Iran_var.get(), self.Sweden_var.get(), self.Austria_var.get(), self.Ukraine_var.get(), self.Taiwan_var.get(), self.Luxembourg_var.get(), self.Brazil_var.get(), self.Uzbekistan_var.get(), self.Croatia_var.get(), self.Turkey_var.get(), self.Serbia_var.get(), self.Kazakhstan_var.get(), self._8_var.get(), self._4_var.get(), self._6_var.get(), self._5_var.get(), self._2_var.get(), self._12_var.get(), self._3_var.get(), self._10_var.get(), self._1_var.get(), self._7_var.get(), self._16_var.get(), self.V_type_var.get(), self.Inline_var.get(), self.Opposed_var.get(), self.W_type_var.get(), self.Rotary_var.get(), variable_names, "advanced", 0, 1, 0, None)

        self.sql_query_textbox = tkinter.Text(self.advanced_frame, height=1, width=10)
        self.execute_button = ttk.Button(self.advanced_frame, text="Import Search", command=execute_sql_query)
        self.clear_button = ttk.Button(self.advanced_frame, text="Clear", command=clear_text)

        self.reset_all_paramaters_button = ttk.Button(self.advanced_frame, text="Reset Paramaters",
                                                      command=self.reset_all_paramaters_advanced_page)
        self.clear_all_checkboxes_button = ttk.Button(self.advanced_frame, text="Clear Checkboxes",
                                                      command=self.clear_all_checkboxes)
        self.show_percentage_of_logged_data = ttk.Button(self.advanced_frame, text="Show Data %",
                                                         command=self.display_percentage_of_logged_data)
        self.search_basic_override_button = ttk.Button(self.advanced_frame, text="Basic Search Override")
        self.search_basic_override_button["command"] = lambda: self.search_by_model_advanced_page(database_path, table_names, self.brand_dropdown2.get(), self.model_dropdown2.get(), round(self.min_year_slider2.get()), round(self.max_year_slider2.get()), round(self.min_seating_capacity_slider.get()), round(self.max_seating_capacity_slider.get()), round(self.min_horsepower_slider.get()), round(self.max_horsepower_slider.get()), round(self.min_weight_slider.get()), round(self.max_weight_slider.get()), round(self.min_powertoweight_slider.get(), 2), round(self.max_powertoweight_slider.get(), 2), round(self.min_displacement_slider.get()), round(self.max_displacement_slider.get()), round(self.min_top_speed_slider.get()), round(self.max_top_speed_slider.get()), self.engine_placement_front_var.get(), self.engine_placement_mid_var.get(), self.engine_placement_rear_var.get(), self.fuel_type_gasoline_var.get(), self.fuel_type_diesel_var.get(), self.fuel_type_hybrid_var.get(), self.fuel_type_electric_var.get(), self.fuel_type_other_var.get(), self.drivetrain_fwd_var.get(), self.drivetrain_rwd_var.get(), self.drivetrain_awd_var.get(), self.car_type_roadster_var.get(), self.car_type_coupe_var.get(), self.car_type_hatchback_var.get(), self.car_type_spyder_var.get(), self.car_type_cabriolet_var.get(), self.car_type_sedan_var.get(), self.car_type_wagon_var.get(), self.car_type_suv_var.get(), self.car_type_pickup_var.get(), self.car_type_van_var.get(), self.car_type_limousine_var.get(), self.transmission_manual_var.get(), self.transmission_automatic_var.get(), self.bore_stroke_ratio_undersquare_var.get(), self.bore_stroke_ratio_square_var.get(), self.bore_stroke_ratio_oversquare_var.get(), self.United_Kingdom_var.get(), self.Japan_var.get(), self.Germany_var.get(), self.Italy_var.get(), self.France_var.get(), self.United_States_var.get(), self.Belgium_var.get(), self.Romania_var.get(), self.South_Korea_var.get(), self.Russia_var.get(), self.Switzerland_var.get(), self.China_var.get(), self.India_var.get(), self.Latvia_var.get(), self.Fictional_var.get(), self.Malaysia_var.get(), self.Netherlands_var.get(), self.Poland_var.get(), self.Czech_Republic_var.get(), self.Spain_var.get(), self.Australia_var.get(), self.Iran_var.get(), self.Sweden_var.get(), self.Austria_var.get(), self.Ukraine_var.get(), self.Taiwan_var.get(), self.Luxembourg_var.get(), self.Brazil_var.get(), self.Uzbekistan_var.get(), self.Croatia_var.get(), self.Turkey_var.get(), self.Serbia_var.get(), self.Kazakhstan_var.get(), self._8_var.get(), self._4_var.get(), self._6_var.get(), self._5_var.get(), self._2_var.get(), self._12_var.get(), self._3_var.get(), self._10_var.get(), self._1_var.get(), self._7_var.get(), self._16_var.get(), self.V_type_var.get(), self.Inline_var.get(), self.Opposed_var.get(), self.W_type_var.get(), self.Rotary_var.get(), variable_names, "simple", 0, 0, 0, None)

        self.search_advanced_button = ttk.Button(self.advanced_frame, text="Advanced Search")
        self.search_advanced_button["command"] = lambda: self.search_by_model_advanced_page(database_path, table_names, self.brand_dropdown2.get(), self.model_dropdown2.get(), round(self.min_year_slider2.get()), round(self.max_year_slider2.get()), round(self.min_seating_capacity_slider.get()), round(self.max_seating_capacity_slider.get()), round(self.min_horsepower_slider.get()), round(self.max_horsepower_slider.get()), round(self.min_weight_slider.get()), round(self.max_weight_slider.get()), round(self.min_powertoweight_slider.get(), 2), round(self.max_powertoweight_slider.get(), 2), round(self.min_displacement_slider.get()), round(self.max_displacement_slider.get()), round(self.min_top_speed_slider.get()), round(self.max_top_speed_slider.get()), self.engine_placement_front_var.get(), self.engine_placement_mid_var.get(), self.engine_placement_rear_var.get(), self.fuel_type_gasoline_var.get(), self.fuel_type_diesel_var.get(), self.fuel_type_hybrid_var.get(), self.fuel_type_electric_var.get(), self.fuel_type_other_var.get(), self.drivetrain_fwd_var.get(), self.drivetrain_rwd_var.get(), self.drivetrain_awd_var.get(), self.car_type_roadster_var.get(), self.car_type_coupe_var.get(), self.car_type_hatchback_var.get(), self.car_type_spyder_var.get(), self.car_type_cabriolet_var.get(), self.car_type_sedan_var.get(), self.car_type_wagon_var.get(), self.car_type_suv_var.get(), self.car_type_pickup_var.get(), self.car_type_van_var.get(), self.car_type_limousine_var.get(), self.transmission_manual_var.get(), self.transmission_automatic_var.get(), self.bore_stroke_ratio_undersquare_var.get(), self.bore_stroke_ratio_square_var.get(), self.bore_stroke_ratio_oversquare_var.get(), self.United_Kingdom_var.get(), self.Japan_var.get(), self.Germany_var.get(), self.Italy_var.get(), self.France_var.get(), self.United_States_var.get(), self.Belgium_var.get(), self.Romania_var.get(), self.South_Korea_var.get(), self.Russia_var.get(), self.Switzerland_var.get(), self.China_var.get(), self.India_var.get(), self.Latvia_var.get(), self.Fictional_var.get(), self.Malaysia_var.get(), self.Netherlands_var.get(), self.Poland_var.get(), self.Czech_Republic_var.get(), self.Spain_var.get(), self.Australia_var.get(), self.Iran_var.get(), self.Sweden_var.get(), self.Austria_var.get(), self.Ukraine_var.get(), self.Taiwan_var.get(), self.Luxembourg_var.get(), self.Brazil_var.get(), self.Uzbekistan_var.get(), self.Croatia_var.get(), self.Turkey_var.get(), self.Serbia_var.get(), self.Kazakhstan_var.get(), self._8_var.get(), self._4_var.get(), self._6_var.get(), self._5_var.get(), self._2_var.get(), self._12_var.get(), self._3_var.get(), self._10_var.get(), self._1_var.get(), self._7_var.get(), self._16_var.get(), self.V_type_var.get(), self.Inline_var.get(), self.Opposed_var.get(), self.W_type_var.get(), self.Rotary_var.get(), variable_names, "advanced", 0, 0, 0, None)

        self.results_label2 = ttk.Label(self.advanced_frame, text="Results:")
        self.results_text2 = tkinter.Text(self.advanced_frame, height=30, width=50)

        # Layout for advanced page
        self.advanced_label.grid()
        self.return_button.grid()

        self.brand_label2.grid()
        self.brand_dropdown2.grid()
        self.model_label2.grid()
        self.model_dropdown2.grid()
        self.min_year_label2.grid()
        self.min_year_slider2.grid()
        self.max_year_label2.grid()
        self.max_year_slider2.grid()
        self.min_seating_capacity_label.grid()
        self.min_seating_capacity_slider.grid()
        self.max_seating_capacity_label.grid()
        self.max_seating_capacity_slider.grid()
        self.min_horsepower_label.grid()
        self.min_horsepower_slider.grid()
        self.max_horsepower_label.grid()
        self.max_horsepower_slider.grid()
        self.min_weight_label.grid()
        self.min_weight_slider.grid()
        self.max_weight_label.grid()
        self.max_weight_slider.grid()
        self.min_powertoweight_label.grid()
        self.min_powertoweight_slider.grid()
        self.max_powertoweight_label.grid()
        self.max_powertoweight_slider.grid()
        self.min_displacement_label.grid()
        self.min_displacement_slider.grid()
        self.max_displacement_label.grid()
        self.max_displacement_slider.grid()
        self.min_top_speed_label.grid()
        self.min_top_speed_slider.grid()
        self.max_top_speed_label.grid()
        self.max_top_speed_slider.grid()
        self.results_label2.grid(column=3, columnspan=2, row=0)
        self.results_text2.grid(column=3, columnspan=2, rowspan=30, row=0)

        # Layout for checkboxes
        self.engine_placement_label.grid(column=2, row=0)
        self.engine_placement_front.grid(column=2, row=1)
        self.engine_placement_mid.grid(column=2, row=2)
        self.engine_placement_rear.grid(column=2, row=3)

        self.fuel_type_label.grid(column=2, row=4)
        self.fuel_type_gasoline.grid(column=2, row=5)
        self.fuel_type_diesel.grid(column=2, row=6)
        self.fuel_type_electric.grid(column=2, row=7)
        self.fuel_type_hybrid.grid(column=2, row=8)
        self.fuel_type_other.grid(column=2, row=9)

        self.body_type_label.grid(column=2, row=10)
        count = 11
        for checkbox in self.body_type_checkboxes:
            checkbox.grid(column=2, row=count)
            count += 1

        self.drivetrain_label.grid(column=2, row=22)
        self.drivetrain_fwd.grid(column=2, row=23)
        self.drivetrain_rwd.grid(column=2, row=24)
        self.drivetrain_awd.grid(column=2, row=25)

        self.transmission_label.grid(column=2, row=26)
        self.transmission_manual.grid(column=2, row=27)
        self.transmission_automatic.grid(column=2, row=28)
        self.bore_stroke_ratio_label.grid(column=2, row=29)
        self.bore_stroke_ratio_oversquare.grid(column=2, row=30)
        self.bore_stroke_ratio_square.grid(column=2, row=31)
        self.bore_stroke_ratio_undersquare.grid(column=2, row=32)
        self.open_countries_page_button.grid(column=2, row=33)
        self.open_engine_layout_page_button.grid(column=2, row=34)

        self.clear_all_checkboxes_button.grid(column=3, row=28)
        self.reset_all_paramaters_button.grid(column=3, row=29)
        self.show_percentage_of_logged_data.grid(column=3, row=30)
        self.find_image_button.grid(column=4, row=28)
        self.go_to_website.grid(column=4, row=29)
        self.search_advanced_button.grid(column=3, row=33)
        self.search_basic_override_button.grid(column=3, row=34)
        self.export_to_CSV_button.grid(column=4, row=30)
        self.export_sql_query_button.grid(column=4, row=31)
        self.sql_query_textbox.grid(column=4, row=32)
        self.execute_button.grid(column=4, row=33)
        self.clear_button.grid(column=4, row=34)

        # Hide advanced page initially
        self.advanced_frame.grid_forget()

        self.reset_all_paramaters_advanced_page()

    # This method shows the percentage of commonly used data logged in cars. This is important, as if a user were to sort a car by its
    #   horsepower properties, they should be aware that a few cars will get left out, as they don't have said information logged in their row
    def display_percentage_of_logged_data(self):

        columns = [
            "year_from", "year_to", "series", "number_of_seats",
            "curb_weight_kg", "cylinder_layout", "number_of_cylinders", "engine_type",
            "cylinder_bore_mm", "stroke_cycle_mm", "engine_placement",
            "capacity_cm3", "engine_hp", "drive_wheels", "transmission", "max_speed_km_per_h",
            ]

        column_counts = {}

        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            # Get the total number of records in the database
            cursor.execute("SELECT COUNT(*) FROM car_db_metric")
            total_records = cursor.fetchone()[0]

            # Execute the SQL queries and calculate percentages
            for column in columns:
                query = f"SELECT COUNT({column}) FROM car_db_metric WHERE {column} IS NOT NULL;"
                cursor.execute(query)
                result = cursor.fetchone()[0]
                percentage = (result / total_records) * 100 if total_records > 0 else 0
                column_counts[column] = percentage

            # Sort the results based on the percentages
            sorted_columns = sorted(column_counts.items(), key=lambda x: x[1], reverse=True)

            # Create a new Tkinter window for displaying the percentages
            popup = Toplevel(self.root)
            popup.title("% of Cars Containing Data;")

            # Create a text widget to display the results
            text_widget = tkinter.Text(popup, height=20, width=50)
            text_widget.pack()

            # Insert the sorted results with percentages into the text widget
            for column, percentage in sorted_columns:
                text_widget.insert(tkinter.END, f"{column}: {percentage:.2f}%\n")

            # Disable text editing in the text widget
            text_widget.configure(state='disabled')

    # Opens the countries of origin page, so that the user can use checkboxes to select cars by countries of manufacturing
    def create_country_of_origin_page(self):
        # Create a new window for country of origin information

        global countries_frame

        try:
            if countries_frame:
                countries_frame.lift()
        except:

            countries_frame = Toplevel(self.root)
            countries_frame.title("Countries of Origin")
            countries_frame.configure(bg='#e0dcd4')

            # Create a frame for country of origin information within the new window
            countries_frame_inner = ttk.Frame(countries_frame)

            # Widgets for country of origin page
            countries_label = ttk.Label(countries_frame_inner, text="Countries of Origin")
            countries_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)  # Place the label at the top

            countries = [
                "United Kingdom", "Japan", "Germany", "Italy", "France", "United States",
                "Belgium", "Romania", "South Korea", "Russia", "Switzerland", "China",
                "India", "Latvia", "Fictional", "Malaysia", "Netherlands", "Poland",
                "Czech Republic", "Spain", "Australia", "Iran", "Sweden", "Austria",
                "Ukraine", "Taiwan", "Luxembourg", "Brazil", "Uzbekistan", "Croatia",
                "Turkey", "Serbia", "Kazakhstan"
                ]

            num_countries = len(countries)
            # Divide countries into two columns
            column1_countries = countries[:num_countries // 2]
            column2_countries = countries[num_countries // 2:]

            # Create Checkbuttons for the first column
            for idx, country in enumerate(column1_countries, start=1):
                # Access the corresponding IntVar instance for the country and assign it to the Checkbutton variable
                var = getattr(self, f"{country.replace(' ', '_')}_var")
                ttk.Checkbutton(countries_frame_inner, text=country, variable=var).grid(row=idx, column=0, sticky='w')

            # Create Checkbuttons for the second column
            for idx, country in enumerate(column2_countries, start=1):
                # Access the corresponding IntVar instance for the country and assign it to the Checkbutton variable
                var = getattr(self, f"{country.replace(' ', '_')}_var")
                ttk.Checkbutton(countries_frame_inner, text=country, variable=var).grid(row=idx, column=1, sticky='w')

            # Create a frame for the buttons
            button_frame = ttk.Frame(countries_frame_inner)
            button_frame.grid(row=num_countries // 2 + 1, columnspan=2, pady=10)

            # Method to reset all country checkboxes within the country selector page
            def clear_checkboxes():
                for country in countries:
                    var = getattr(self, f"{country.replace(' ', '_')}_var")
                    var.set(0)

            # Method to clear all country checkboxes within the country selector page
            def reset_checkboxes():
                for country in countries:
                    var = getattr(self, f"{country.replace(' ', '_')}_var")
                    var.set(1)

            # Button to reset countries checkboxes
            reset_button = ttk.Button(button_frame, text="Reset Countries Checkboxes", command=reset_checkboxes)
            reset_button.grid(row=0, column=0, padx=5)

            # Button to clear countries checkboxes
            clear_button = ttk.Button(button_frame, text="Clear Countries Checkboxes", command=clear_checkboxes)
            clear_button.grid(row=0, column=1, padx=5)

            # Grid layout adjustments for better structure
            countries_frame_inner.grid(row=0, column=0, padx=20, pady=20)

    # Opens the engine layout selector page, where a user can sort a car based on its engine properties, such as a V6, Opposed (Boxer) 4, etc.
    def create_engine_layout_selector_page(self):

        global engine_layout_selector_frame

        try:
            if engine_layout_selector_frame:
                engine_layout_selector_frame.lift()
        except:

            engine_layout_selector_frame = Toplevel(self.root)
            engine_layout_selector_frame.title("Engine Layout Selector")
            engine_layout_selector_frame.configure(bg='#e0dcd4')

            engine_layout_selector_frame_inner = ttk.Frame(engine_layout_selector_frame)
            engine_layout_selector_frame_inner.grid()  # Use pack or grid method to place the frame

            # Widgets for country of origin page
            countries_label = ttk.Label(engine_layout_selector_frame_inner, text="Engine Layout Selector")
            countries_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)  # Place the label at the top

            cylinder_count = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16]

            engine_type = [
                "V-type",  # "V-type with small angle",
                "Inline",  # "inline",
                "Opposed",  # "opposed"
                "W-type",
                "Rotary",  # "rotor",
                ]

            # Create Checkbuttons for cylinder count
            for idx, number in enumerate(cylinder_count, start=1):
                var = getattr(self, f"_{number}_var")
                ttk.Checkbutton(engine_layout_selector_frame_inner, text=number, variable=var).grid(row=idx, column=0, sticky='w')

            # Create Checkbuttons for engine type
            for idx, layout in enumerate(engine_type, start=1):
                valid_layout_name = layout.replace(' ', '_').replace('-', '_')
                var = getattr(self, f"{valid_layout_name}_var")
                ttk.Checkbutton(engine_layout_selector_frame_inner, text=layout, variable=var).grid(row=idx, column=1, sticky='w')
            # Create a frame for the buttons
            button_frame = ttk.Frame(engine_layout_selector_frame_inner)

            if len(engine_type) < len(cylinder_count):
                rowlength = len(cylinder_count) + 1
            else:
                rowlength = len(engine_type) + 1

            button_frame.grid(row=rowlength, columnspan=2, pady=10)

            # Method to reset all checkboxes within the engine selector page
            def clear_checkboxes():
                for number in cylinder_count:
                    var = getattr(self, f"_{number}_var")
                    var.set(0)
                for layout in engine_type:
                    var = getattr(self, f"{layout.replace(' ', '_').replace('-', '_')}_var")
                    var.set(0)

            # Method to set all checkboxes within the engine selector page
            def reset_checkboxes():
                for number in cylinder_count:
                    var = getattr(self, f"_{number}_var")
                    var.set(1)
                for layout in engine_type:
                    var = getattr(self, f"{layout.replace(' ', '_').replace('-', '_')}_var")
                    var.set(1)

            # Button to reset countries checkboxes
            reset_button = ttk.Button(button_frame, text="Reset Layout Checkboxes", command=reset_checkboxes)
            reset_button.grid(row=0, column=0, padx=5)

            # Button to clear countries checkboxes
            clear_button = ttk.Button(button_frame, text="Clear Layout Checkboxes", command=clear_checkboxes)
            clear_button.grid(row=0, column=1, padx=5)

            # Grid layout adjustments for better structure
            engine_layout_selector_frame_inner.grid(row=0, column=0, padx=20, pady=20)

    # Method to search and display models of cars with Google images API
    def search_and_display_mosaic(self, search_query, images_num):

        Success = False
        displayed_images = 0
        displayed_urls = set()
        failed_urls = set()
        rows = 2
        columns = 3

        # Create a new Tkinter window for displaying images
        google_image_search_api_frame = Toplevel(self.root)
        google_image_search_api_frame.title("Google Image Popup")  # Set the title for the new window
        google_image_search_api_frame.minsize(300, 200)  # Set a minimum size for the window

        google_image_search_api_frame_inner = ttk.Frame(google_image_search_api_frame)
        google_image_search_api_frame_inner.grid()  # Use pack or grid method to place the frame

        new_images_num = images_num

        while Success is False and displayed_images < images_num:

            search_params = {
                'q': f'{search_query}',
                'num': new_images_num,  # Number of images to retrieve
                'safe': 'high',  # Safety level of search results (high, medium, or off)
                }

            # print(search_query)

            # Create GoogleImagesSearch object
            gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

            # Search for images
            gis.search(search_params=search_params)

            # Create a grid layout to display images
            rows = 2
            columns = 3

            for i, result in enumerate(gis.results()):
                if displayed_images >= images_num:
                    break

                url = result.url
                if url in displayed_urls or url in failed_urls:
                    continue  # Skip already displayed or failed URLs
                # print(f"Processing URL: {url}")  # Print the URL to verify

                attempts = 0
                max_attempts = 1  # Set a maximum number of attempts to process the image
                timeout_duration = 5  # Set the timeout duration in seconds

                while attempts < max_attempts:
                    try:
                        response = requests.get(url, timeout=timeout_duration)  # Set timeout for the request
                        response.raise_for_status()  # Raise an error for HTTP response errors

                        img = Image.open(BytesIO(response.content))
                        if img.format is None:
                            raise IOError("Image format cannot be identified")

                        img.thumbnail((300, 300))
                        img_tk = ImageTk.PhotoImage(img)

                        label = ttk.Label(google_image_search_api_frame_inner, image=img_tk)
                        label.image = img_tk
                        label.grid(row=displayed_images // columns, column=displayed_images % columns)

                        displayed_images += 1
                        displayed_urls.add(url)  # Track displayed URLs
                        break

                    except (IOError, OSError, UnidentifiedImageError, requests.RequestException) as e:
                        # Uncomment for debugging purposes
                        # print(f"Error processing image at {url}: {e}")
                        attempts += 1
                        new_images_num += 1
                        failed_urls.add(url)
                        # time.sleep(1)  # Add a small delay before retrying

                if displayed_images >= images_num:
                    break  # Break the loop if the required number of images are displayed

        if displayed_images == 0:
            google_image_search_api_frame.minsize(300, 200)  # Set minimum size if no images found
            # Create placeholder labels to fill the grid
            for i in range(rows * columns):
                placeholder_label = ttk.Label(google_image_search_api_frame_inner, text="No Image Found")
                placeholder_label.grid(row=i // columns, column=i % columns)

    def check_internet_connection(self):
        try:
            requests.get('https://www.google.com', timeout=5)  # Send a simple GET request to Google
            return True  # Internet is available
        except requests.ConnectionError:
            return False  # Internet is not available

    def on_find_image_button_click(self, complexity):

        # Check for internet connection
        if not self.check_internet_connection():
            messagebox.showerror("No Internet", "Please check your internet connection.")
            return  # Exit the method if there's no internet

        if complexity == 'basic':

            brand = self.brand_dropdown.get()
            model = self.model_dropdown.get()
            min_year = round(self.min_year_slider.get())
            max_year = round(self.max_year_slider.get())

            if not brand or not model:
                # If either brand or model is empty, show a warning
                messagebox.showwarning("Missing Information", "Please enter both Brand and Model.")
                return  # Exit the method without performing the search

            if min_year == get_min_max_year(database_path, table_names, "min") and max_year == get_min_max_year(database_path, table_names, "max"):
                # Dates are equal to defaults, create search query without dates
                search_query = f"{brand} {model} car"
            else:
                # Dates are different from defaults, create search query with dates
                search_query = f"{brand} {model} {min_year}-{max_year} car"

            # Call the search and display method with the constructed search query
            self.search_and_display_mosaic(search_query, 1)

        elif complexity == 'advanced':

            brand = self.brand_dropdown2.get()
            model = self.model_dropdown2.get()
            min_year = round(self.min_year_slider2.get())
            max_year = round(self.max_year_slider2.get())

            if not brand or not model:
                # If either brand or model is empty, show a warning
                messagebox.showwarning("Missing Information", "Please enter both Brand and Model.")
                return  # Exit the method without performing the search

            if min_year == get_min_max_year(database_path, table_names, "min") and max_year == get_min_max_year(database_path, table_names, "max"):
                # Dates are equal to defaults, create search query without dates
                search_query = f"{brand} {model} car"
            else:
                # Dates are different from defaults, create search query with dates
                search_query = f"{brand} {model} {min_year}-{max_year} car"

            # Create a Toplevel window to contain the slider and checkbox
            dialog = tkinter.Toplevel(self.root)
            dialog.title("Image Options")

            scale_frame = ttk.Frame(dialog)
            scale_frame.pack()

            num_images_var = tkinter.IntVar()
            self.modified_param = ''

            def on_modify_parameter(self):
                # Handle modifying the search parameter here
                modified_param = simpledialog.askstring("Modify Parameter", "Enter the modified search parameter:")
                if modified_param is None:
                    return
                else:
                    # Store the modified parameter in the class instance attribute
                    self.modified_param = modified_param

            def update_image_slider_label(value):
                try:
                    image_slider_label.config(text=f"Number of Images: {int(math.ceil(float(value)))}")
                except ValueError:
                    pass

            def scale_changed(value):
                update_image_slider_label(value)

            def on_okay(num_images_var, search_query):  # Receive search_query as an argument
                num_images_val = int(math.ceil(float(num_images_var.get())))
                dialog.destroy()

                # For example:
                # print("NUM IMAGES VAL", num_images_val)

                # Call the search and display method with the constructed search query and number of images

                self.search_and_display_mosaic(f"{search_query} {self.modified_param}", num_images_val)

            image_slider_label = ttk.Label(scale_frame, text="Number of Images: 1")
            image_slider_label.pack()

            num_images_var = tkinter.DoubleVar()  # Use DoubleVar for float values
            scale = ttk.Scale(dialog, from_=1, to=6, orient=tkinter.HORIZONTAL, variable=num_images_var, command=scale_changed)
            scale.set(1)
            scale.pack()

            modify_search = tkinter.IntVar()
            check_button = ttk.Checkbutton(dialog, text="Modify Search Parameter", variable=modify_search, command=lambda: on_modify_parameter(self))
            check_button.pack()

            okay_button = ttk.Button(dialog, text="OK", command=lambda: on_okay(num_images_var, search_query))  # Pass search_query
            okay_button.pack()

            dialog.transient(self.root)  # Set parent window

            # Make the main window wait for the dialog to be closed before continuing
            self.root.wait_window(dialog)

    # Updates the model dropdown for the advanced page
    def update_model_dropdown2(self, event):
        selected_brand = self.brand_dropdown2.get()
        if selected_brand.strip() != '':
            models = search_by_brand_show_model_only(database_path, table_names, selected_brand)
            self.model_dropdown2['values'] = models
        else:
            self.model_dropdown2['values'] = None
            self.model_dropdown2.set("")

    # Shows main page
    def show_main_page(self):
        self.main_frame.grid()
        self.advanced_frame.grid_forget()

    # Shows advanced page
    def show_advanced_page(self):
        self.advanced_frame.grid()
        self.main_frame.grid_forget()

    # Function that when executed opens the website of the manufactuer in the user's default chosen browser
    def go_to_make_website(self, page):

        brand = ''
        if page == 'basic':
            brand = self.brand_dropdown.get()
        elif page == 'advanced':
            brand = self.brand_dropdown2.get()

        if not brand:
            # If brand is empty, show a warning
            messagebox.showwarning("Missing Information", "Please enter Brand.")
            return False  # Exit the method without performing the search

        website_url = None  # Initialize website_url with None
        success_flag = False  # Initialize success_flag with False

        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            # Add quotes around the {brand} placeholder in the SQL query
            search_query = f"SELECT website FROM {table_names} WHERE make = '{brand}'"
            cursor.execute(search_query)
            result = cursor.fetchone()
            if result and result[0] is not None and result[0] != '':
                website_url = result[0]
                webbrowser.open(website_url)  # Opens the website in default browser
                success_flag = True  # Indicates success
            else:
                messagebox.showwarning("Website not found", "No website found for the selected brand.")
                success_flag = False  # Indicates failure

        if success_flag:
            return success_flag
        elif not success_flag and website_url is not None:
            messagebox.showwarning("Unable to open Website", f"{website_url}.")
            return success_flag
        else:
            return success_flag


#  Function used to show all brands (makes), used in brand dropdown boxes
def print_brand_names_only(database_path, table_name):
    try:
        with sqlite3.connect(database_path) as connection:
            # Connects to the SQL database and create a cursor
            cursor = connection.cursor()
            cursor.execute(f"SELECT make FROM {table_name}")
            rows = cursor.fetchall()

            brandlist = []

            if rows:

                # Sets automatically exclude duplicates
                unique_brands = set()

                # Add rows but without parentheses or similar
                for row in rows:
                    unique_brands.add(row[0])

                # Sort the list alphanumerically so that it can be printed
                for brand in sorted(unique_brands):
                    brandlist.append(brand)

            return brandlist  # Return the list of brand names

    except Exception as e:
        print(f"An error has occurred: {str(e)}")
        return []


# The search_by_model function is always called to search, it's one function that manages everything and returns the results in a formatted string and the amount of cars found.
def search_by_model(database_path, table_name, brand, model, year_from, year_to, seating_capacity_min, seating_capacity_max, engine_hp_min, engine_hp_max, curb_weight_kg_min, curb_weight_kg_max, min_power_to_weight_ratio, max_power_to_weight_ratio, displacement_min, displacement_max, top_speed_min, top_speed_max, engine_front_bool, engine_mid_bool, engine_rear_bool, gasoline_bool, diesel_bool, hybrid_bool, electric_bool, other_fuel_type_bool, drivetrain_fwd_bool, drivetrain_rwd_bool, drivetrain_awd_bool, car_type_roadster_bool, car_type_coupe_bool, car_type_hatchback_bool, car_type_spyder_bool, car_type_cabriolet_bool, car_type_sedan_bool, car_type_wagon_bool, car_type_suv_bool, car_type_pickup_bool, car_type_van_bool, car_type_limousine_bool, manual_transmission_bool, automatic_transmission_bool, Bore_Stroke_Undersquare_bool, Bore_Stroke_Square_bool, Bore_Stroke_Oversquare_bool, United_Kingdom_bool, Japan_bool, Germany_bool, Italy_bool, France_bool, United_States_bool, Belgium_bool, Romania_bool, South_Korea_bool, Russia_bool, Switzerland_bool, China_bool, India_bool, Latvia_bool, Fictional_bool, Malaysia_bool, Netherlands_bool, Poland_bool, Czech_Republic_bool, Spain_bool, Australia_bool, Iran_bool, Sweden_bool, Austria_bool, Ukraine_bool, Taiwan_bool, Luxembourg_bool, Brazil_bool, Uzbekistan_bool, Croatia_bool, Turkey_bool, Serbia_bool, Kazakhstan_bool, _8_cylinders_bool, _4_cylinders_bool, _6_cylinders_bool, _5_cylinders_bool, _2_cylinders_bool, _12_cylinders_bool, _3_cylinders_bool, _10_cylinders_bool, _1_cylinders_bool, _7_cylinders_bool, _16_cylinders_bool, V_type_engine_layout_bool, Inline_engine_layout_bool, Opposed_engine_layout_bool, W_type_engine_layout_bool, Rotary_engine_layout_bool, variable_names, complexity, export_results_to_csv_bool, query_export_bool, query_import_boolean, query):
    # If the user wishes to export their results to a csv, this function opens a file and writes the data
    def export_results_to_csv(file_path, rows):
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([i[0] for i in cursor.description])  # Write headers
                writer.writerows(rows)  # Write query results
            return True
        except Exception as e:
            print("Error occurred while exporting to CSV:", e)
            return False

    parameters = {
        'database_path': database_path,
        'table_name': table_name,
        'brand': brand,
        'model': model,
        'year_from': year_from,
        'year_to': year_to,
        'seating_capacity_min': seating_capacity_min,
        'seating_capacity_max': seating_capacity_max,
        'engine_hp_min': engine_hp_min,
        'engine_hp_max': engine_hp_max,
        'curb_weight_kg_min': curb_weight_kg_min,
        'curb_weight_kg_max': curb_weight_kg_max,
        'min_power_to_weight_ratio': min_power_to_weight_ratio,
        'max_power_to_weight_ratio': max_power_to_weight_ratio,
        'displacement_min': displacement_min,
        'displacement_max': displacement_max,
        'top_speed_min': top_speed_min,
        'top_speed_max': top_speed_max,
        'engine_front_bool': engine_front_bool,
        'engine_mid_bool': engine_mid_bool,
        'engine_rear_bool': engine_rear_bool,
        'gasoline_bool': gasoline_bool,
        'diesel_bool': diesel_bool,
        'hybrid_bool': hybrid_bool,
        'electric_bool': electric_bool,
        'other_fuel_type_bool': other_fuel_type_bool,
        'drivetrain_fwd_bool': drivetrain_fwd_bool,
        'drivetrain_rwd_bool': drivetrain_rwd_bool,
        'drivetrain_awd_bool': drivetrain_awd_bool,
        'car_type_coupe_bool': car_type_coupe_bool,
        'car_type_roadster_bool': car_type_roadster_bool,
        'car_type_hatchback_bool': car_type_hatchback_bool,
        'car_type_spyder_bool': car_type_spyder_bool,
        'car_type_cabriolet_bool': car_type_cabriolet_bool,
        'car_type_sedan_bool': car_type_sedan_bool,
        'car_type_wagon_bool': car_type_wagon_bool,
        'car_type_suv_bool': car_type_suv_bool,
        'car_type_pickup_bool': car_type_pickup_bool,
        'car_type_van_bool': car_type_van_bool,
        'car_type_limousine_bool': car_type_limousine_bool,
        'manual_transmission_bool': manual_transmission_bool,
        'automatic_transmission_bool': automatic_transmission_bool,
        'Bore_Stroke_Undersquare_bool': Bore_Stroke_Undersquare_bool,
        'Bore_Stroke_Square_bool': Bore_Stroke_Square_bool,
        'Bore_Stroke_Oversquare_bool': Bore_Stroke_Oversquare_bool,
        'United_Kingdom_bool': United_Kingdom_bool,
        'Japan_bool': Japan_bool,
        'Germany_bool': Germany_bool,
        'Italy_bool': Italy_bool,
        'France_bool': France_bool,
        'United_States_bool': United_States_bool,
        'Belgium_bool': Belgium_bool,
        'Romania_bool': Romania_bool,
        'South_Korea_bool': South_Korea_bool,
        'Russia_bool': Russia_bool,
        'Switzerland_bool': Switzerland_bool,
        'China_bool': China_bool,
        'India_bool': India_bool,
        'Latvia_bool': Latvia_bool,
        'Fictional_bool': Fictional_bool,
        'Malaysia_bool': Malaysia_bool,
        'Netherlands_bool': Netherlands_bool,
        'Poland_bool': Poland_bool,
        'Czech_Republic_bool': Czech_Republic_bool,
        'Spain_bool': Spain_bool,
        'Australia_bool': Australia_bool,
        'Iran_bool': Iran_bool,
        'Sweden_bool': Sweden_bool,
        'Austria_bool': Austria_bool,
        'Ukraine_bool': Ukraine_bool,
        'Taiwan_bool': Taiwan_bool,
        'Luxembourg_bool': Luxembourg_bool,
        'Brazil_bool': Brazil_bool,
        'Uzbekistan_bool': Uzbekistan_bool,
        'Croatia_bool': Croatia_bool,
        'Turkey_bool': Turkey_bool,
        'Serbia_bool': Serbia_bool,
        'Kazakhstan_bool': Kazakhstan_bool,
        '_1_cylinders_bool': _1_cylinders_bool,
        '_2_cylinders_bool': _2_cylinders_bool,
        '_3_cylinders_bool': _3_cylinders_bool,
        '_4_cylinders_bool': _4_cylinders_bool,
        '_5_cylinders_bool': _5_cylinders_bool,
        '_6_cylinders_bool': _6_cylinders_bool,
        '_7_cylinders_bool': _7_cylinders_bool,
        '_8_cylinders_bool': _8_cylinders_bool,
        '_10_cylinders_bool': _10_cylinders_bool,
        '_12_cylinders_bool': _12_cylinders_bool,
        '_16_cylinders_bool': _16_cylinders_bool,
        'V_type_engine_layout_bool': V_type_engine_layout_bool,
        'Inline_engine_layout_bool': Inline_engine_layout_bool,
        'Opposed_engine_layout_bool': Opposed_engine_layout_bool,
        'W_type_engine_layout_bool': W_type_engine_layout_bool,
        'Rotary_engine_layout_bool': Rotary_engine_layout_bool,
        'variable_names': variable_names,
        'complexity': complexity,
        'export_results_to_csv_bool': export_results_to_csv_bool,
        'query_export_bool': query_export_bool,
        'query_import_boolean': query_import_boolean,
        'query': query,

        }

    # Uncomment for debugging purposes
    # print("Parameters:")
    # for param_name, param_value in parameters.items():
    # print(f"{param_name}: {param_value}")

    # This large amount of conditionals all append to arrays which later form a single SQL query as a string, executing the search in one go
    #   This makes the program extremely fast and efficient, as SQL has a logarithmic search time, and performing a single search is very fast
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()

            # Base query
            base_query = f"SELECT * FROM {table_name}"

            # Call the method and store the result
            result = sort_car_series_column_by_keywords(database_path, table_names, car_body_categories)

            # and_paramaters and _and conditions are for searches that should be cars that have x and x and x (such as a V8 AND 400 horsepower AND less than 1200 kilos)
            # or paramater are conditions that can be or such as Japanese Or Italian OR German car
            and_paramaters = []
            and_conditions = []
            or_paramaters = []
            or_conditions = []

            if brand is not None and brand.strip() != "":
                and_conditions.append("make = ?")
                and_paramaters.append(brand)
            if model is not None and model.strip() != "":
                and_conditions.append("model = ?")
                and_paramaters.append(model)
            if year_from > year_to:
                messagebox.showerror("Error", "'Year From' must be less than 'Year To'")
            if year_from is not None and year_from != get_min_max_year(database_path, table_names, "min"):
                and_conditions.append("year_from >= ? AND year_from != 0.0")
                and_paramaters.append(year_from)
            if year_to is not None and year_to != get_min_max_year(database_path, table_names, "max"):
                and_conditions.append("year_to <= ? AND year_to != 0.0")
                and_paramaters.append(year_to)
            if seating_capacity_min is not None and seating_capacity_min != get_min_max_seating_capacity("min", database_path, table_names) and seating_capacity_max is not None and seating_capacity_max != get_min_max_seating_capacity("max", database_path, table_names):
                and_conditions.append("CAST(number_of_seats AS INTEGER) >= ? AND CAST(number_of_seats AS INTEGER) <= ?")
                and_paramaters.extend([int(round(seating_capacity_min)), int(round(seating_capacity_max))])
            elif seating_capacity_min is not None and seating_capacity_min != get_min_max_seating_capacity("min", database_path, table_names):
                and_conditions.append("CAST(number_of_seats AS INTEGER) >= ?")
                and_paramaters.append(int(round(seating_capacity_min)))
            elif seating_capacity_max is not None and seating_capacity_max != get_min_max_seating_capacity("max", database_path, table_names):
                and_conditions.append("CAST(number_of_seats AS INTEGER) <= ?")
                and_paramaters.append(int(round(seating_capacity_max)))
            if engine_hp_min is not None and engine_hp_min != get_min_max_engine_hp("min", database_path, table_names):
                and_conditions.append("engine_hp >= ?")
                and_paramaters.append(int(engine_hp_min))
            if engine_hp_max is not None and engine_hp_max != get_min_max_engine_hp("max", database_path, table_names):
                and_conditions.append("engine_hp <= ?")
                and_paramaters.append(int(engine_hp_max))
            if curb_weight_kg_min is not None and curb_weight_kg_min != get_min_max_curb_weight("min", database_path, table_names):
                and_conditions.append("curb_weight_kg >= ?")
                and_paramaters.append(int(curb_weight_kg_min))
            if curb_weight_kg_max is not None and curb_weight_kg_max != get_min_max_curb_weight("max", database_path, table_names):
                and_conditions.append("curb_weight_kg <= ?")
                and_paramaters.append(int(curb_weight_kg_max))
            if min_power_to_weight_ratio is not None and min_power_to_weight_ratio != get_min_max_power_to_weight_ratio(
                    "min", database_path, table_names):
                and_conditions.append("engine_hp / NULLIF(curb_weight_kg, 0) >= ?")
                and_paramaters.append(min_power_to_weight_ratio)
            if max_power_to_weight_ratio is not None and max_power_to_weight_ratio != get_min_max_power_to_weight_ratio(
                    "max", database_path, table_names):
                and_conditions.append("engine_hp / NULLIF(curb_weight_kg, 0) <= ?")
                and_paramaters.append(max_power_to_weight_ratio)
            if displacement_min is not None and displacement_min != get_min_max_displacement("min", database_path, table_names):
                and_conditions.append("capacity_cm3 >= ?")
                and_paramaters.append(displacement_min)
            if displacement_max is not None and displacement_max != get_min_max_displacement("max", database_path, table_names):
                and_conditions.append("capacity_cm3 <= ?")
                and_paramaters.append(displacement_max)

            db_top_speed_min = get_min_max_top_speed('min', database_path, table_names)
            db_top_speed_max = get_min_max_top_speed('max', database_path, table_names)

            if top_speed_min is not None and top_speed_min != db_top_speed_min:
                and_conditions.append("CAST(REPLACE(REPLACE(max_speed_km_per_h, ' km/h', ''), ',', '') AS REAL) >= ? AND max_speed_km_per_h NOT LIKE '%km/h%'")
                and_paramaters.append(top_speed_min)

            if top_speed_max is not None and top_speed_max != db_top_speed_max:
                and_conditions.append("CAST(REPLACE(REPLACE(max_speed_km_per_h, ' km/h', ''), ',', '') AS REAL) <= ? AND max_speed_km_per_h NOT LIKE '%km/h%'")
                and_paramaters.append(top_speed_max)

            # Checkboxes:
            if gasoline_bool == 1 and diesel_bool == 1 and hybrid_bool == 1 and electric_bool == 1 and other_fuel_type_bool == 1:
                pass
            else:
                fuel_type_conditions = []
                if gasoline_bool == 1:
                    fuel_type_conditions.append("engine_type IN (?, ?, ?, ?, ?, ?)")
                    or_paramaters.extend(["Gasoline", "petrol", "Gas", "Gasoline, Gas", "Rotor", "Petrol"])
                if diesel_bool == 1:
                    fuel_type_conditions.append("engine_type IN (?, ?)")
                    or_paramaters.extend(["Diesel", "diesel"])
                if hybrid_bool == 1:
                    fuel_type_conditions.append("engine_type IN (?, ?)")
                    or_paramaters.extend(["Hybrid", "hybrid"])
                if electric_bool == 1:
                    fuel_type_conditions.append("engine_type = ?")
                    or_paramaters.append("Electric")
                if other_fuel_type_bool == 1:
                    fuel_type_conditions.append("engine_type = ?")
                    or_paramaters.append("Liquefied coal hydrogen gases")

                if fuel_type_conditions:
                    and_conditions.append(f"({' OR '.join(fuel_type_conditions)})")

            if engine_front_bool == 1 and engine_mid_bool == 1 and engine_rear_bool == 1:
                pass
            else:
                engine_placement_conditions = []
                if engine_front_bool == 1:
                    engine_placement_conditions.append("engine_placement IN (?, ?, ?, ?)")
                    or_paramaters.extend(
                        ["front, cross-section", "front, longitudinal", "Front", "Front, longitudinally"])
                if engine_mid_bool == 1:
                    engine_placement_conditions.append("engine_placement IN (?, ?)")
                    or_paramaters.extend(["mid-engine", "central"])
                if engine_rear_bool == 1:
                    engine_placement_conditions.append("engine_placement IN (?)")
                    or_paramaters.append("rear")

                if engine_placement_conditions:
                    and_conditions.append(f"({' OR '.join(engine_placement_conditions)})")

            if drivetrain_fwd_bool == 1 and drivetrain_rwd_bool == 1 and drivetrain_awd_bool == 1:
                pass
            else:
                drivetrain_conditions = []
                if drivetrain_fwd_bool == 1:
                    drivetrain_conditions.append("drive_wheels = ?")
                    or_paramaters.append("Front wheel drive")
                if drivetrain_rwd_bool == 1:
                    drivetrain_conditions.append("drive_wheels = ?")
                    or_paramaters.append("Rear wheel drive")
                if drivetrain_awd_bool == 1:
                    drivetrain_conditions.append("drive_wheels IN (?, ?, ?, ?)")
                    or_paramaters.extend(
                        ["full", "All wheel drive (AWD)", "Four wheel drive (4WD)", "Constant all wheel drive"])

                if drivetrain_conditions:
                    and_conditions.append(f"({' OR '.join(drivetrain_conditions)})")

            if manual_transmission_bool == 1 and automatic_transmission_bool:
                pass
            else:
                transmission_conditions = []
                if manual_transmission_bool == 1:
                    transmission_conditions.append("transmission = ?")
                    or_paramaters.append("Manual")

                if automatic_transmission_bool == 1:
                    transmission_conditions.append("transmission IN (?, ?, ?, ?, ?)")
                    or_paramaters.extend(
                        ["Automatic", "robot", "Continuously variable transmission (CVT)", "Electronic with 1 clutch",
                         "Electronic with 2 clutch"])

                if transmission_conditions:
                    and_conditions.append(f"({' OR '.join(transmission_conditions)})")

            if Bore_Stroke_Undersquare_bool == 1 and Bore_Stroke_Square_bool == 1 and Bore_Stroke_Oversquare_bool == 1:
                pass
            else:
                bore_stroke_ratio_conditions = []
                tolerance = 0.01  # Define a tolerance value for the comparison

                if Bore_Stroke_Undersquare_bool == 1:
                    bore_stroke_ratio_conditions.append("(cylinder_bore_mm / stroke_cycle_mm < ?) AND (cylinder_bore_mm != stroke_cycle_mm) AND (cylinder_bore_mm < "
                                                        "stroke_cycle_mm)")  # Define undersquare condition
                    or_paramaters.append(1 + tolerance)  # Add tolerance to the condition

                if Bore_Stroke_Square_bool == 1:
                    bore_stroke_ratio_conditions.append("(cylinder_bore_mm = stroke_cycle_mm)")

                if Bore_Stroke_Oversquare_bool == 1:
                    bore_stroke_ratio_conditions.append("(cylinder_bore_mm / stroke_cycle_mm > ?) AND (cylinder_bore_mm != stroke_cycle_mm) AND (cylinder_bore_mm > "
                                                        "stroke_cycle_mm)")  # Define oversquare condition
                    or_paramaters.append(1 - tolerance)  # Add tolerance to the condition

                if bore_stroke_ratio_conditions:
                    and_conditions.append(f"({' OR '.join(bore_stroke_ratio_conditions)})")

            if United_Kingdom_bool == 1 and Japan_bool == 1 and Germany_bool == 1 and Italy_bool == 1 and France_bool == 1 and United_States_bool == 1 and Belgium_bool == 1 and Romania_bool == 1 and South_Korea_bool == 1 and Russia_bool == 1 and Switzerland_bool == 1 and China_bool == 1 and India_bool == 1 and Latvia_bool == 1 and Fictional_bool == 1 and Malaysia_bool == 1 and Netherlands_bool == 1 and Poland_bool == 1 and Czech_Republic_bool == 1 and Spain_bool == 1 and Australia_bool == 1 and Iran_bool == 1 and Sweden_bool == 1 and Austria_bool == 1 and Ukraine_bool == 1 and Taiwan_bool == 1 and Luxembourg_bool == 1 and Brazil_bool == 1 and Uzbekistan_bool == 1 and Croatia_bool == 1 and Turkey_bool == 1 and Serbia_bool == 1 and Kazakhstan_bool == 1:
                pass
            else:
                nationality_conditions = []

                if United_Kingdom_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("United Kingdom")

                if Japan_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Japan")

                if Germany_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Germany")

                if Italy_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Italy")

                if France_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("France")

                if United_States_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("United States")

                if Belgium_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Belgium")

                if Romania_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Romania")

                if South_Korea_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("South Korea")

                if Russia_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Russia")

                if Switzerland_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Switzerland")

                if China_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("China")

                if India_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("India")

                if Latvia_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Latvia")

                if Fictional_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Fictional")

                if Malaysia_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Malaysia")

                if Netherlands_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Netherlands")

                if Poland_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Poland")

                if Czech_Republic_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Czech Republic")

                if Spain_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Spain")

                if Australia_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Australia")

                if Iran_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Iran")

                if Sweden_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Sweden")

                if Austria_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Austria")

                if Ukraine_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Ukraine")

                if Taiwan_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Taiwan")

                if Luxembourg_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Luxembourg")

                if Brazil_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Brazil")

                if Uzbekistan_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Uzbekistan")

                if Croatia_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Croatia")

                if Turkey_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Turkey")

                if Serbia_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Serbia")

                if Kazakhstan_bool == 1:
                    nationality_conditions.append("country_of_origin == ?")
                    or_paramaters.append("Kazakhstan")

                if nationality_conditions:
                    and_conditions.append(f"({' OR '.join(nationality_conditions)})")

            if _1_cylinders_bool == 1 and _2_cylinders_bool == 1 and _3_cylinders_bool == 1 and _4_cylinders_bool == 1 and _5_cylinders_bool == 1 and _6_cylinders_bool == 1 and _7_cylinders_bool == 1 and _8_cylinders_bool == 1 and _10_cylinders_bool == 1 and _12_cylinders_bool == 1 and _16_cylinders_bool == 1:
                pass
            else:
                cylinder_count_conditions = []

                cylinder_count_list = [
                    [_1_cylinders_bool, 1],
                    [_2_cylinders_bool, 2],
                    [_3_cylinders_bool, 3],
                    [_4_cylinders_bool, 4],
                    [_5_cylinders_bool, 5],
                    [_6_cylinders_bool, 6],
                    [_7_cylinders_bool, 7],
                    [_8_cylinders_bool, 8],
                    [_10_cylinders_bool, 10],
                    [_12_cylinders_bool, 12],
                    [_16_cylinders_bool, 16]
                    ]
                for cylinder, count in cylinder_count_list:
                    if cylinder == 1:
                        cylinder_count_conditions.append("number_of_cylinders = ?")
                        or_paramaters.append(count)

                if cylinder_count_conditions:
                    and_conditions.append(f"({' OR '.join(cylinder_count_conditions)})")

            # Assuming 'and_conditions', 'or_conditions', 'or_parameters' are predefined lists or variables

            if V_type_engine_layout_bool == 1 and Inline_engine_layout_bool == 1 and Opposed_engine_layout_bool == 1 and W_type_engine_layout_bool == 1 and Rotary_engine_layout_bool == 1:
                pass
            else:
                engine_layout_conditions = []

                if V_type_engine_layout_bool == 1:
                    engine_layout_conditions.append("cylinder_layout IN (?, ?)")
                    or_paramaters.extend(["V-type", "V-type with small angle"])

                if Inline_engine_layout_bool == 1:
                    engine_layout_conditions.append("cylinder_layout IN (?, ?)")
                    or_paramaters.extend(["Inline", "inline"])

                if Opposed_engine_layout_bool == 1:
                    engine_layout_conditions.append("cylinder_layout IN (?, ?)")
                    or_paramaters.extend(["Opposed", "opposed"])

                if W_type_engine_layout_bool == 1:
                    engine_layout_conditions.append("cylinder_layout = ?")
                    or_paramaters.append("W-type")

                # if drivetrain_fwd_bool == 1:
                #     drivetrain_conditions.append("drive_wheels = ?")
                #     or_paramaters.append("Front wheel drive")
                # if drivetrain_rwd_bool == 1:
                #     drivetrain_conditions.append("drive_wheels = ?")
                #     or_paramaters.append("Rear wheel drive")
                # if drivetrain_awd_bool == 1:
                #     drivetrain_conditions.append("drive_wheels IN (?, ?, ?, ?)")
                #     or_paramaters.extend(
                #         ["full", "All wheel drive (AWD)", "Four wheel drive (4WD)", "Constant all wheel drive"])

                if Rotary_engine_layout_bool == 1:
                    engine_layout_conditions.append("cylinder_layout IN (?, ?)")
                    or_paramaters.extend(["Rotary", "rotor"])

                if engine_layout_conditions:
                    and_conditions.append(f"({' OR '.join(engine_layout_conditions)})")

            #     "V-type",  # "V-type with small angle",
            #     "Inline",  # "inline",
            #     "Opposed",  # "opposed"
            #     "W-type",
            #     "Rotary",  # "rotor",

            # ALWAYS PUT THIS ONE LAST
            if car_type_roadster_bool == 1 and car_type_coupe_bool == 1 and car_type_hatchback_bool == 1 and car_type_spyder_bool == 1 and car_type_suv_bool == 1 and car_type_van_bool == 1 and car_type_cabriolet_bool == 1 and car_type_sedan_bool == 1 and car_type_wagon_bool == 1 and car_type_pickup_bool == 1 and car_type_limousine_bool == 1:
                pass
            else:
                if car_type_roadster_bool == 1:
                    for category, models in result.items():
                        if category == "Roadster":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_coupe_bool == 1:
                    for category, models in result.items():
                        if category == "Coupe":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_hatchback_bool == 1:
                    for category, models in result.items():
                        if category == "Hatchback":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_spyder_bool == 1:
                    for category, models in result.items():
                        if category == "Spyder":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_suv_bool == 1:
                    for category, models in result.items():
                        if category == "SUV":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_van_bool == 1:
                    for category, models in result.items():
                        if category == "Van":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_cabriolet_bool == 1:
                    for category, models in result.items():
                        if category == "Cabriolet":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_sedan_bool == 1:
                    for category, models in result.items():
                        if category == "Sedan":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_wagon_bool == 1:
                    for category, models in result.items():
                        if category == "Wagon":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_pickup_bool == 1:
                    for category, models in result.items():
                        if category == "Pickup":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

                if car_type_limousine_bool == 1:
                    for category, models in result.items():
                        if category == "Limousine":
                            or_conditions.append(f"series IN ({','.join(['?'] * len(models))})")
                            or_paramaters.extend(models)

            if query_import_boolean == 1:
                try:
                    # print("QUERY FOR IMPORT:", query)

                    # Execute the query with parameters
                    cursor.execute(query)

                except Exception as e:
                    print("Error handling imported query:", e)
                    print("QUERY FOR IMPORT:", query)

            else:
                try:

                    if and_conditions or or_conditions:
                        and_clause = " AND ".join(and_conditions)
                        or_clause = " OR ".join(or_conditions)
                        if and_clause and or_clause:
                            where_clause = f"({and_clause}) AND ({or_clause})"
                        else:
                            where_clause = and_clause if and_clause else or_clause

                        search_query = f"{base_query} WHERE {where_clause}"
                        parameters = and_paramaters + or_paramaters

                        # print("SQL Query:", search_query)
                        # print("paramaters:", parameters)

                        cursor.execute(search_query, tuple(parameters))
                    else:
                        cursor.execute(base_query)

                except sqlite3.Error as e:
                    print("Error executing query:", e)

            if query_export_bool == 1:
                try:
                    if search_query is not None:
                        query_str = search_query
                        for param in parameters:
                            # Replace the first occurrence of '?' in the query with the parameter value
                            query_str = query_str.replace('?', repr(param), 1)
                        # print("Executed Statement:", query_str)
                except:
                    query_str = base_query
                popup = tkinter.Toplevel()
                popup.title("Execute Statement")

                label = ttk.Label(popup, text="Execute Statement:")
                label.pack()

                text = tkinter.Text(popup, height=5, width=50)
                text.insert(tkinter.END, query_str)
                text.pack()

            rows = cursor.fetchall()

            # CSV conditional
            if export_results_to_csv_bool == 1:
                # Create a method to open a file dialog for directory selection
                def choose_directory():
                    root = tkinter.Tk()
                    root.withdraw()  # Hide the root window

                    chosen_directory = filedialog.askdirectory()
                    return chosen_directory

                # Choose the directory for exporting the CSV file
                chosen_directory = choose_directory()

                if chosen_directory:
                    file_path = chosen_directory + "/results.csv"  # Define the file path with a file name
                    export_success = export_results_to_csv(file_path, rows)
                    if export_success:
                        #  print(f"Results exported to {file_path}")
                        pass
                    else:
                        print("Failed to export results to CSV")
                else:
                    # print("No directory selected. CSV export cancelled.")
                    pass

            count = 0
            skip_counter = 0
            if len(rows) > 0:
                formatted_output = ""
                for row in rows:
                    for i in range(1, len(variable_names)):
                        if skip_counter > 0:
                            skip_counter -= 1
                            continue

                        if complexity == "simple" and row[i] is not None:
                            if variable_names[i - 1][1] is True:
                                formatted_output += f"{variable_names[i - 1][0]}{row[i]}\n"
                        elif complexity == "advanced" and row[i] is not None:
                            if (variable_names[i - 1][0] == 'Engine HP: ') and (
                                    variable_names[i - 1 + 1][0] == 'Engine HP RPM: ') and (row[i] is not None) and (
                                    row[i + 1] is not None):
                                formatted_output += f"{variable_names[i - 1][0]}{row[i]} @ {row[i + 1]} RPM\n"
                                skip_counter += 1
                            if (variable_names[i - 1][0] == 'Maximum Torque (N*m): ') and (
                                    variable_names[i - 1 + 1][0] == 'Turnover of Maximum Torque (rpm): ') and (
                                    row[i] is not None) and (row[i + 1] is not None):
                                formatted_output += f"{variable_names[i - 1][0]}{row[i]} @ {row[i + 1]} RPM\n"
                                skip_counter += 1
                            if skip_counter == 0:
                                formatted_output += f"{variable_names[i - 1][0]}{row[i]}\n"
                    formatted_output += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
                    count += 1
                # Uncomment for debugging purposes (slows down program somewhat)
                # print(formatted_output)
                # print("NUMBER OF RESULTS: ", count)
                return formatted_output, count

            try:
                # Uncomment for debugging purposes
                pass
                # print("SQL Query:", search_query)
                # print("paramaters:", parameters)
            except:
                pass

    except sqlite3.Error as e:
        # Uncomment for debugging purposes
        # print("An error occurred in the search_by_model:", e)
        pass

    return (f"There was an error OR no results were found\n")


# Runs the program
if __name__ == "__main__":
    # GUI Attempt
    TkinterRoot = tkinter.Tk()
    CarSortApp = CarSortGUI(TkinterRoot)
    TkinterRoot.configure(bg='#f0ece4')
    apply_ttk_theme()
    TkinterRoot.mainloop()
