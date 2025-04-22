


import DATA_FILE
import EXE



def show_data(data, title = "EnneadTab Data Visualization", show_axis=True):
    """
    primary_value is the value that used to constantly display.
    {
    "title": "My Data Visualization",
    "x_axis_title": "x", # this
    "y_axis_title": "y", # and this
    "primary_value_title": "primary_value", # and this line are to tell which key to abstract for each function, think of this as the definitoin to each of the data item
    "data": [
        {
            "x": 10,
            "y": 10,
            "attributes": {
                "primary_value": 1
            }
        },
        {
            "x": 2,
            "y": 15,
            "attributes": {
                "primary_value": 2
            }
        },
        {
            "x": 2,
            "y": 10,
            "attributes": {
                "primary_value":10
            }
        }
    ]
}"""
    data_package = {
        "title": title,
        "x_axis_title": "x",
        "y_axis_title": "y",
        "primary_value_title": "primary_value",
        "show_axis_title": show_axis,
        "show_axis_increment": show_axis,
        "data": data
    }




    DATA_FILE.set_data(data_package, "interactive_chart_data")

    EXE.try_open_app("Data_Viz")


if __name__ == "__main__":
    show_data({
    "title": "My Data Visualization",
    "x_axis_title": "x", # this
    "y_axis_title": "y", # and this
    "primary_value_title": "primary_value", # and this line are to tell which key to abstract for each function, think of this as the definitoin to each of the data item
    "data": [
        {
            "x": 10,
            "y": 10,
            "attributes": {
                "primary_value": 1
            }
        },
        {
            "x": 2,
            "y": 15,
            "attributes": {
                "primary_value": 2
            }
        },
        {
            "x": 2,
            "y": 10,
            "attributes": {
                "primary_value":10
            }
        }
    ]
})