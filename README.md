# DataLoader: A Versatile Tool for Geospatial Data Processing

The `DataLoader` Python class is a powerful tool designed to handle geospatial data, particularly for working with satellite imagery in TIFF format. This class streamlines the integration of satellite images with corresponding information from a CSV file, making it a valuable asset for various applications, from agricultural analysis to environmental monitoring.

## Key Features

- **Efficient Data Loading**: The class can load raster images and extract specific regions of interest based on provided polygon coordinates, using the `rasterio` library.
- **Comprehensive Data Handling**: The `load_coordinates` method reads a CSV file containing essential details such as geographic coordinates, crop labels, and dates related to the satellite images.
- **Color Band Selection**: The `select_color` method identifies the color band (e.g., red, blue, green, or NIR) being processed, which is crucial for vegetation analysis.
- **Temporal Analysis**: The `get_date_from_path` method extracts date information from the image file paths, enabling temporal analysis of crop growth.
- **NDVI Calculation**: The core `load_tiff` function reads TIFF images, computes the NDVI (Normalized Difference Vegetation Index), and structures the data into a pandas DataFrame.
- **Data Cleanup and Interpolation**: Methods such as `reshape_dataframe` and `linear_interpolation_missing_dates` ensure data consistency and evenly spaced temporal data, critical for meaningful analysis.

## Installation and Usage

1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/your-username/DataLoader.git
   ```

2. Make sure you have the required dependencies installed. You can use `pip` to install them:

   ```shell
   pip install rasterio pandas shapely numpy
   ```

3. To use the `DataLoader` class, import it into your Python script:

   ```python
   from DataLoader import DataLoader
   ```

4. Create an instance of the `DataLoader` class, specifying the path to the directory containing your TIFF images and the CSV file with coordinates:

   ```python
   obj = DataLoader()
   obj.load_tiff("images/red/")
   ```

5. The processed data will be available in a pandas DataFrame. You can access it using the `get_df` method:

   ```python
   data_frame = obj.get_df()
   ```

6. For further analysis or visualization, you can save the DataFrame to a CSV file:

   ```python
   data_frame.to_csv("processed_data.csv", index=False)
   ```

## Conclusion and Improvements

The `DataLoader` class provides a solid foundation for handling geospatial data from satellite images. However, to make it even more robust and user-friendly, consider adding comprehensive error handling to gracefully handle various scenarios, such as missing files or incorrect data formats. Additionally, enhancing the visualization capabilities would greatly improve the value of this tool, allowing users to gain deeper insights from the processed geospatial data.

## Potential Uses

This tool has a wide range of potential applications:

- **Agricultural Analysis**: Monitor crop growth, detect anomalies, and analyze agricultural patterns over time.
- **Environmental Monitoring**: Assess the health of vegetation, detect changes in land use, and track the impact of environmental factors.
- **Research**: Researchers in fields such as ecology, agriculture, and geography can use this tool to analyze geospatial data for their studies.

By leveraging the capabilities of the `DataLoader` class, researchers, farmers, environmental scientists, and other professionals can gain valuable insights from processed geospatial data.