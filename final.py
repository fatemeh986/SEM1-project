import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtGui, QtWidgets
from sample3 import Ui_MainWindow  
import pdb
from matplotlib.figure import Figure
import requests
import folium
from contextlib import redirect_stdout
from io import StringIO
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from contextlib import redirect_stdout



class DataHandler:
    def __init__(self):
        pass

    def clean_data(self, file_path):
        try:
            df = pd.read_excel(file_path)
        
            # Cleaning Data
            df = df.drop_duplicates()
            df = df.drop(columns=["Region", "ISO3", "Reference", "Number and type of monitoring stations",
                                  "PM25 temporal coverage (%)", "PM10 temporal coverage (%)", "NO2 temporal coverage (%)"])
            df = df[~df['Year'].isin(range(2000, 2010)) & ~df['Year'].isin(range(2020, 2024))]
        
            return df
        except Exception as e:
            print("Error cleaning data:", e)
            return None

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.data_handler = DataHandler()
        self.dataframe = None
        self.current_plot = None
        self.year_plot = None
        self.country_plot = None

        self.ui.Select.clicked.connect(self.select_file)
        self.ui.pbPlot.clicked.connect(self.plot_selected_pollutant)
        self.ui.PlotTab1.clicked.connect(self.plot_mean_pollutants_by_year)
        self.ui.cbYTab1.currentIndexChanged.connect(self.update_year_plot)
        self.ui.pbPlot_3.clicked.connect(self.plot_country_pollutants)
        self.ui.pbPlot_2.clicked.connect(self.plot_selected_countries_pollutants)  # Added this line


        self.load_years()

    def select_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx)")

        if file_path:
            self.dataframe = self.data_handler.clean_data(file_path)
            self.ui.DataName.setText(file_path)
            self.load_pollutants()
            self.load_years()
            self.load_countries_tab3()
            self.setup_tab2()

    def load_pollutants(self):
        if self.dataframe is not None:
            pollutants = [col for col in self.dataframe.columns if any(poll in col for poll in ['NO2', 'PM2.5', 'PM10'])]
            self.ui.choosePollutant1.clear()
            self.ui.choosePollutant1.addItems(pollutants)

    def load_years(self):
        if self.dataframe is not None:
            years_2010_to_2019 = self.dataframe[self.dataframe['Year'].between(2010, 2019)]['Year'].unique()
            self.ui.cbYTab1.clear()
            self.ui.cbYTab1.addItems([str(year) for year in years_2010_to_2019])

    def load_countries_tab3(self):
        if self.dataframe is not None:
            countries = self.dataframe['Country'].unique()
            self.ui.cbCountTab3.clear()
            self.ui.cbCountTab3.addItems(countries)

    def plot_selected_pollutant(self):
        if self.dataframe is None:
            return

        selected_pollutant = self.ui.choosePollutant1.currentText()
        mean_value = self.dataframe.groupby('Country')[selected_pollutant].mean().nlargest(20)

        if self.current_plot:
            self.ui.verticalLayout_9.removeWidget(self.current_plot)
            self.current_plot.deleteLater()
            self.current_plot = None

        new_plot = plt.figure(figsize=(6, 6))
        ax = new_plot.add_subplot(111)
        ax.bar(mean_value.index, mean_value.values)
        ax.set_title(f'Top 20 Countries for {selected_pollutant}')
        ax.set_xlabel('Countries')
        ax.set_ylabel('Mean Pollutant Level')
        ax.tick_params(axis='x', rotation=90)
        ax.figure.tight_layout()

        canvas = FigureCanvas(new_plot)
        self.ui.verticalLayout_9.addWidget(canvas)
        self.ui.verticalLayout_9.update()
        self.current_plot = canvas

    def plot_mean_pollutants_by_country_year(self, dataframe, pollutant_column, constant_means):
        if self.year_plot:
            self.ui.verticalLayout_7.removeWidget(self.year_plot)
            self.year_plot.deleteLater()
            self.year_plot = None

        mean_value = dataframe.groupby(['Country', 'Year'])[pollutant_column].mean().reset_index()
        top20_country_year = mean_value.groupby('Year').apply(lambda x: x.nlargest(20, pollutant_column)).reset_index(drop=True)

        for year, data in top20_country_year.groupby('Year'):
            plt.figure(figsize=(6, 6))
            plt.bar(data['Country'], data[pollutant_column], label='Top 20 Countries', alpha=0.7)

            for idx, (mean_val, custom_label, line_style) in enumerate(constant_means):
                linestyle = '-' if line_style == 'solid' else '--'
                plt.axhline(y=mean_val, color='red', linestyle=linestyle, label=custom_label)

            plt.title(f'Top 20 Polluted Countries for {pollutant_column} in {year}')
            plt.xlabel('Countries')
            plt.ylabel(pollutant_column)
            plt.legend()
            plt.xticks(rotation=90)
            plt.tight_layout()

            canvas = FigureCanvas(plt.gcf())
            self.ui.verticalLayout_7.addWidget(canvas)
            self.ui.verticalLayout_7.update()
            self.year_plot = canvas

    def plot_mean_pollutants_by_year(self):
        if self.dataframe is None:
            return

        selected_pollutant = self.ui.choosePollutant1.currentText()
        selected_year = int(self.ui.cbYTab1.currentText())

        pollutants_means = {
            'NO2 (μg/m3)': [(40, '2005 AQG', 'solid'), (10, 'Revised in 2021 AQG', 'dashed')],
            'PM2.5 (μg/m3)': [(10, '2005 AQG', 'solid'), (5, 'Revised in 2021 AQG', 'dashed')],
            'PM10 (μg/m3)': [(20, '2005 AQG(20)', 'solid'), (15, 'Revised in 2021 AQG(15)', 'dashed')]
        }

        plot_data = pollutants_means.get(selected_pollutant)

        if plot_data:
            if self.year_plot:
                self.ui.verticalLayout_7.removeWidget(self.year_plot)
                self.year_plot.deleteLater()
                self.year_plot = None

            self.plot_mean_pollutants_by_country_year(
                self.dataframe[self.dataframe['Year'] == selected_year],
                selected_pollutant,
                plot_data
            )

    def update_year_plot(self):
        if self.year_plot:
            self.ui.verticalLayout_7.removeWidget(self.year_plot)
            self.year_plot.deleteLater()
            self.year_plot = None
            self.plot_mean_pollutants_by_year()

    def plot_pollutants_for_each_country(self):
        if self.dataframe is None:
            return

        selected_country = self.ui.cbCountTab3.currentText()
        pollutant_columns = ['NO2 (μg/m3)', 'PM2.5 (μg/m3)', 'PM10 (μg/m3)']

        plt.figure(figsize=(8, 5))

        country_data = self.dataframe[self.dataframe['Country'] == selected_country]
        grouped_data = country_data.groupby('Year')[pollutant_columns].mean().reset_index()

        years = grouped_data['Year']

        for pollutant_column in pollutant_columns:
            mean_values = grouped_data[pollutant_column]
            plt.plot(years, mean_values, marker='o', label=pollutant_column)

        plt.xlabel('Years')
        plt.ylabel('Mean Value')
        plt.title(f'Mean Values of Pollutants for {selected_country}')
        plt.legend()
        plt.tight_layout()

        if self.country_plot:
            self.ui.verticalLayout_16.removeWidget(self.country_plot)
            self.country_plot.deleteLater()
            self.country_plot = None

        canvas = FigureCanvas(plt.gcf())
        self.ui.verticalLayout_16.addWidget(canvas)
        self.ui.verticalLayout_16.update()
        self.country_plot = canvas

    def plot_country_pollutants(self):
        self.plot_pollutants_for_each_country()

    def load_countries_to_listview(self):
        if self.dataframe is not None:
            countries = self.dataframe['Country'].unique()
            model = QtGui.QStandardItemModel()
            for country in countries:
                item = QtGui.QStandardItem(country)
                item.setCheckable(True)
                model.appendRow(item)
            self.ui.listView.setModel(model)



    def plot_selected_countries_pollutants(self):
        selected_countries = []
        model = self.ui.listView.model()
        for row in range(model.rowCount()):
            item = model.item(row)
            if item.checkState() == QtCore.Qt.Checked:
                selected_countries.append(item.text())
        selected_year = int(self.ui.cbYTab2.currentText())
        selected_pollutant = self.ui.PollutTab2.currentText()
    
        if not selected_countries:  # No countries selected
            return
    
        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
    
        # Replace the existing loop with the new logic
        for country in selected_countries:
            country_data = self.dataframe[
                (self.dataframe['Country'] == country) & (self.dataframe['Year'] == selected_year)]
    
            # New logic starts here
            if len(country_data[selected_pollutant].values) > 0:
                try:
                    ax.bar(country, country_data[selected_pollutant].values[0], label=country)
                except IndexError as e:
                    # Handle the IndexError here
                    print(f"IndexError occurred for {country} and {selected_pollutant}: {e}")
                    # You can add other actions or error handling here
            else:
                # Handle the case where the array is empty
                print(f"No data available for {country} and {selected_pollutant}")
            # New logic ends here
    
        ax.set_xlabel('Countries')
        ax.set_ylabel(selected_pollutant)
        ax.set_title(f'{selected_pollutant} for Selected Countries in {selected_year}')
        ax.legend()
        fig.tight_layout()
    
        self.update_plot_in_tab2(fig)


    

    def update_plot_in_tab2(self, plot):
        if self.country_plot:
            self.ui.verticalLayout_14.removeWidget(self.country_plot)
            self.country_plot.deleteLater()
            self.country_plot = None

        canvas = FigureCanvas(plot)
        self.ui.verticalLayout_14.addWidget(canvas)
        self.ui.verticalLayout_14.update()
        self.country_plot = canvas

    def connect_tab2_buttons(self):
        self.ui.pbPlot_2.clicked.connect(self.plot_selected_countries_pollutants)

    def setup_tab2(self):
        self.load_countries_to_listview()
        self.load_years_tab2()
        self.load_pollutants_tab2()
        self.connect_tab2_buttons()

    def load_years_tab2(self):
        if self.dataframe is not None:
            years = self.dataframe['Year'].unique()
            self.ui.cbYTab2.clear()
            self.ui.cbYTab2.addItems([str(year) for year in years])

    def load_pollutants_tab2(self):
        pollutants = ['NO2 (μg/m3)', 'PM2.5 (μg/m3)', 'PM10 (μg/m3)']
        self.ui.PollutTab2.clear()
        self.ui.PollutTab2.addItems(pollutants)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

