
import rasterio.mask
import rasterio.features
import rasterio.warp
import os
import pandas as pd
from shapely.geometry import Polygon
import ast
import numpy as np
from _datetime import datetime, timedelta
class data_loader():
    def __init__(self, path_dir=""):
        self.path_dir = path_dir
        self.df = pd.DataFrame()
        self.color = ""
        pass


    def load_rasterio(self,image_path="",polygon_list=[]):
        ''' Load a raster image and return a numpy array '''

        
        #get polygon from list of coordinates
        shape = Polygon(polygon_list)
        # print(shape)
        

        with rasterio.open(image_path) as src:
            
            # Read the dataset's valid data mask as a ndarray.
            mask = src.dataset_mask()

            # Extract feature shapes and values from the array.
            data, transform = rasterio.mask.mask(
            src,
            [shape],
            crop=False,
            nodata=float('nan'),
            # pad=True,
        )
        return data




        # return df_partial


    def load_coordinates(self,csv_path = ""):
        df = pd.read_csv(csv_path)
        #from dataframe, only get the Coordinates
        coordinates = df['Coordinates']
        crop_label = df['Crop']
        dates_sowing = df['Sowing Date']
        dates_harvesting = df['Harvest Date']

        #convert to list
        coordinates = coordinates.tolist()
        # for coordinate,crop in zip(coordinates,crop_label):
        for coordinate,crop,date_sowing,date_harvesting in zip(coordinates,crop_label,dates_sowing,dates_harvesting):
            #conver string representation of list to list
            coordinate = ast.literal_eval(coordinate)
            #reverse each coordinate pair from lat, long to long, lat, not very accurate but will do for now
            coordinate = [[long,lat] for lat,long in list(coordinate)]
            yield coordinate,crop,date_sowing,date_harvesting

    def select_color(self,path):
        if "red" in path:
            self.color = "red"
        elif "nir" in path:
            self.color = "nir"
        elif "green" in path:
            self.color = "green"
        elif "blue" in path:
            self.color = "blue"

    def get_date_from_path(self,path):
        return path.split("/")[-1].split(".")[0]

    def load_tiff(self,path_dir):
        print("here")

        for i,crop,date_sowing,date_harvesting in self.load_coordinates("/media/saqib/VolumeD/mywork/engineer-take-home/farms.csv"):

            for root, dir, files in os.walk(path_dir):
                for file in files:
                    #get_date from path and add to be used in dataframe
                    date = self.get_date_from_path(file)

                    #get color from path and add to be used in dataframe
                    color = self.select_color(file)

                    if not file.endswith(".tiff"):
                        continue
                    
                    # print(file)
                    all_color_paths = self.replace_color_path(os.path.join(root,file))
                    
                    data_red = self.load_rasterio(all_color_paths["red"],i)
                    data_blue = self.load_rasterio(all_color_paths["blue"],i)
                    data_green = self.load_rasterio(all_color_paths["green"],i)
                    data_nir = self.load_rasterio(all_color_paths["nir"],i)


                    
                    # flatten the np matrix data_red
                    data_red = data_red.flatten()
                    data_blue = data_blue.flatten()
                    data_green = data_green.flatten()
                    data_nir = data_nir.flatten()
                    
                    #index array the size of data_red
                    index = np.arange(data_red.shape[0])


                    #assert that all the colors are the same size
                    assert data_red.shape == data_blue.shape == data_green.shape == data_nir.shape
                    crop_series = pd.Series([crop]*data_red.shape[0])
                    date_series = pd.Series([date]*data_red.shape[0])
                    date_sowing_series = pd.Series([date_sowing]*data_red.shape[0])
                    date_harvesting_series = pd.Series([date_harvesting]*data_red.shape[0])

                    data_nvdi = pd.Series((data_nir-data_red)/(data_red+data_nir))

                    #create a dataframe with the data
                    df = pd.DataFrame({"pixel":index,
                                        "red":data_red,
                                        "blue":data_blue,
                                        "green":data_green,
                                        "nir":data_nir,
                                        "ndvi":data_nvdi,
                                        "crop":crop_series,
                                        "date":date_series,
                                        "date_sowing":date_sowing_series,
                                        "date_harvesting":date_harvesting_series
                                        },
                                        index=range(data_red.shape[0]))
                    self.df = pd.concat([self.df,df],axis=0,ignore_index=True)
        self.reshape_dataframe()

        self.linear_interpolation_missing_dates()
        np_data = self.df_to_numpy()
        print(np_data)


                    
    def replace_color_path(self,path):
        return {"red":path,
                "blue": path.replace("red","blue"),
                "green": path.replace("red","green"),
                "nir": path.replace("red","nir")}

    def compute_ndvi(self,red, nir):
        ndvi = (nir - red) / (nir + red)
        return ndvi

    def get_df(self):
        # re_df = self.df.set_index(['pixel'])
        return self.df

    def reshape_dataframe(self):
        complete_df= pd.DataFrame()
        for pixel in self.df['pixel'].unique():
            df_pixel = self.df[self.df['pixel']==pixel]
            df_pixel = df_pixel.dropna()
            complete_df = pd.concat([complete_df,df_pixel],axis=0)

        # complete_df.to_csv("complete_df.csv")
        # print(len(self.df))
        # print(len(complete_df))
        #remove all rows where date is not in the sowing and harvesting dates
        complete_df = complete_df[complete_df['date']>=complete_df['date_sowing']]
        complete_df = complete_df[complete_df['date']<=complete_df['date_harvesting']]
        self.df = complete_df

    def linear_interpolation_missing_dates(self):
        #remove all the empty pixels with no data at all
        self.df = self.df.dropna()
        #get all the dates
        dates = self.df['date'].unique()
        pixels = self.df['pixel'].unique()
        
        #sort all dates
        dates = sorted(dates)
        #find difference between consecutive dates using datetime
        date_diff = [datetime.strptime(dates[i+1],'%Y-%m-%d') - datetime.strptime(dates[i],'%Y-%m-%d') for i in range(len(dates)-1)]
        min_diff = min(date_diff)
        print(date_diff)
        #find all dates that are not evenly spaced in time
        dates_to_interpolate = [dates[i] for i in range(len(dates)-1) if date_diff[i] != min_diff]

        # a nested list comprehension
        new_dates = [[datetime.strptime(dates[i],'%Y-%m-%d') + j*min_diff for j in range(1,int(date_diff[i]/min_diff))] for i in range(len(dates)-1) if date_diff[i] != min_diff]
        new_dates = [item.strftime('%Y-%m-%d') for sublist in new_dates for item in sublist]
        #insert all the missing dates in df
        for pixel in pixels:
            df_pixel = self.df[self.df['pixel']==pixel]
            crop_df_pixel = df_pixel['crop'].unique()[0]
            date_sowing_df_pixel = df_pixel['date_sowing'].unique()[0]
            date_harvesting_df_pixel = df_pixel['date_harvesting'].unique()[0]
        #     for date in new_dates:
        #         df_pixel = df_pixel.append({'pixel':pixel,'date':date.strftime('%Y-%m-%d')},ignore_index=True)
        #     self.df = pd.concat([self.df,df_pixel],axis=0)
            df = pd.DataFrame({"pixel":[pixel]*len(new_dates),
                            "red":np.nan,
                            "blue": np.nan,
                            "green": np.nan,
                            "nir":np.nan,
                            "ndvi":np.nan,
                            "crop":[crop_df_pixel]*len(new_dates),
                            "date":new_dates,
                            "date_sowing":[date_sowing_df_pixel]*len(new_dates),
                            "date_harvesting":[date_harvesting_df_pixel]*len(new_dates)
                            },
                            index=range(len(new_dates)))
            self.df = pd.concat([self.df,df],axis=0,ignore_index=True)

        self.df = self.df.sort_values(by=['pixel','date'])
        self.df = self.df.interpolate(method='linear',limit_direction='both')

    def df_to_numpy(self):
        #initialize numpy array
        X = np.array([])
        for pixel in self.df['pixel'].unique():
            df_pixel = self.df[self.df['pixel']==pixel]
            numpy_pixel = df_pixel[["red","blue","green","nir","ndvi"]].to_numpy()
            if X.size == 0:
                self.X = numpy_pixel
            else:
                np.append(self.X,numpy_pixel,axis=0)

        return X
        

if __name__ == "__main__":
    obj = data_loader()
    obj.load_tiff("/media/saqib/VolumeD/mywork/engineer-take-home/images/red/")

    # print(obj.df)
    #group by pixels and date
    obj.get_df().to_csv("data_interpolated.csv",index=False)

#         # print(i)

# #test replace color path function
# obj = data_loader()
# # obj.replace_color_path("/media/saqib/VolumeD/mywork/engineer-take-home/images/2019-01-01_red.tiff")
