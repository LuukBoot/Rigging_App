
# Rigging app 
## Project Description 
This app checks the rigging and the crane according to the DNV standards. According to the DNV standard, the skew load factor is a standard value. With the help of a python script, it is possible to calculate this more in detail. After the calculations are done, with the help of the Viktor program an automatic word document will be generated. The skew load factor is explained in the skewload.md document
First, the rigging checks were made in an excel sheet, with the help of this app it will be more user-friendly.

## Tabl of contents =


1. [ How to install and run the project. ](#install)
2. [ How to use the project. ](#usage)
3. [ App. ](#App)
    1. [ Project Tree. ](#App_tree)
    2. [ Workflowdiagram. ](#App_flow_dia)
    2. [ Data input. ](#App_input)
4. [ Skewload. ](#SKL)
    1. [ Goal. ](#SKL_goal)
    2. [ Data Input. ](#SKL_input)
    3. [ Flowchart. ](#SKL_flow)
    4. [ Start hook point. ](#SKL_start)
5. [ Reccomondation ](#Recommendation)

<a name="install"></a>

## How to install and run the project
Dit moet ik nog uitvogelen aan de hand van de documentatie van viktor

<a name="usage"></a>

## How to use the project 
Ik moet nog een handleiding maken, die komt hier te staan

<a name="App"></a>

## App layout 

### Tree 

See below the tree structure of the app, in the Rigging_app folder are all the python scripts. See below what all files do:
- Calculations: All code for calculations is in this file 
- The controller responds to the user input and performs interactions on the data model objects. The controller receives the input, optionally validates it, and then passes the input to the model.
- The model is responsible for managing the data of the application. It receives user input from the controller
- Default_inputs: This is responsible for transforming the data from the excel file to useful data and is responsible for the standard values of the different tables.
- Folder Data_input: All data input is put in this file
- Folder Data_output: All data output is put in this file
- parametrization: Responsible for creating the frontend of the application

```
app/
┣ Data_input/
┃ ┣ Constants_DNV.xlsx
┃ ┗ Data_lifting_tools.xlsx
┣ Data_output/
┃ ┣ Results_SKL.csv
┃ ┣ Top_view.png
┃ ┗ Word_template.docx
┣ Rigging_app/
┃ ┣ calculations.py
┃ ┣ controller.py
┃ ┣ Default_inputs.py
┃ ┣ model.py
┃ ┣ parametrization.py
┃ ┗ __init__.py
┗ __init__.py
```


### Workflowdiagram 
In this chapter the workflow diagram is described, see below the the total workflow diagram
![This is a image](/Images_read_me/Workflow.jpg)

In the upper part of the figure, the front end of the app is shown. The front end of the app consists of 5 different tabs, each tab has a different kind of input fields and buttons. The parameters that are filled are explained in more detail in the chapter "Input".  On the left side, the databases are shown, Both these databases are excel sheets and the data in these files can easily be changed. With the help of the module openpyxl, the data from the excel sheet is transformed to useful data, in the default_inputs file

<br/><br/>
All the params and data from the excel sheets are passed to the communication class, in the module file. The first thing the class does is change the params into useful data, in which way it is stored can be seen in the next chapter. When all the data is transformed, the calculations are done, These are:

- The cog envelope (Class: Calc_COG_env)
- Load distributie/ Cog shift factor (Class: Calc_load_dis))
- Tilt factor (Class: Tilt factor)
- Calculations of the factors that are descibed in next chapter: tab_3 (Class: Calc_factors)
- Calculated the rigging checks and unity check(Class: Calc_rigging)
- Caluclated crane checks and unity check(Class: Calc_crane)

All the data from the parameters and the data from the results from the calculations are attributed to the communication class, so it can be used in other methods. With the help of the property method, the data can be retrieved, so it can be shown in 3 different tabs( see the part under communication class):

- First tab:
    - Ouput load distributie[t]
    - Output load distributie[%]
    - Output all factors 
- Second tab: Checks rigging
- Third tab: Checks crane 



<br/><br/>
Both the skew load analysis and the make word document are not in the communication class, because every time a params is changed in one of the 5 tabs. The communication class will be activated and those two actions take a lot of time, this is why it is done with the help of buttons. When the skew load analysis button is pressed, first it gets the data from the communication class and it will analyze the skew load factor, when the analysis is done the result will be stored in a CSV file, so it can be retrieved when making the word document. 

<br/><br/>
When the word document button is activated, it takes all data and results from the calculations from the communication class, also the file params. Then based on the lift points and the geometry of the object, a top-view picture is made. These are params such as the date/the project no/ company name.  With the help of the jinja notations, the results and data are transformed into readable rigging check documentation, this word document can be downloaded via the internet and can be changed where necessary. 

### Input 
The front off the app is made with the help of the viktor program, in total there are 5 different input apps: See below:
#### Tab 1
In tab 1 the general information is entered:



- Number of lifting points 
- Coardinates of lifting points 
- COG point 
- Lift object geometry 
- Lift object weight 
- Coardinates of lifting points

With the help of the method make_data_general the data is stored in the structure, that is shown below:

```
Data_general={"Lift_points": [nx[float(point_x),float(point_y),float(point_z)]],
              "Obj_geo": [float(length),float(width),float(height],
              "COG": [float(COG_x),float(COG_y),float(COG_z],
              "LW": float(weight of liftobject)}
```
In de lift points, the n is equal to number of lifting points

#### Tab 2
In tab 2, the values for the Factors, sling safety factor and the skew load factor are entered. In section 1the parameters for the factors are entered, those are:

- Answer weight continency factor
- Answer COG shift factor crane
- Answer COG shift factor rigging
- Answer dynamic amplication factor
- Answer YAW factor
- Angles Tilt factor



With the help of the method make_general factors the data is stored in a diactionary structure, that is shown below:

```
Data_general_factor={"WCF":str(answer),
                        "COGCrane":str(answer),
                        "COG_envelope":str(answer),
                        "DAF":str(answer),
                        "YAW":str(answer),
                        "TEF":[float(Roll angle), float(Pitch angle)],
                        "SKL_analysis": Bool}

```
In section 2 the values for the sling safetry factor are entered, the params are:

- Anwer Lift factor
- Answer Material factor
- Answer Consequence factor
- Answer Wear/application factor

With the help of the method make_data_SSF_factor factors the data is stored in a array with a number of dictionaries that depends on the number of sling safety factors, see below code snippet:

```
Data_sling_safetry=[{"Lift_factor":float(answer),
                     "Consequence_factor":float(answer),
                     "material_factor":str(answer,
                     "Wear_application_factor":str(answer}]

```

The answers for the skew load factor are entered in section 3, see other page.
 
#### Tab 3
In tab 3, the values for the rigging check are entered

- Name of the rigging point
- Material of the sling/grommet
- Which points are connected 
- Rigging weight above the lifting point
- Sling angle with the transverse
- Sling angle with the longitudinal 
- Sling safety factor 
- Termination factor 
- Skew load factor 
- Sldf factor 
- Type sling:
    - Amount of parts 
    - ID(SWL and diameter)
- Connection upper side sling/grommet:
    - Type 
    - Diameter 
    - SWL 
- Connection lower side sling/grommet:
    - Type 
    - Diameter 
    - SWL 

With the help of the method make_data_rigging factors the data is stored in a array with a number of dictionaries that depends on the rigging points that needs to be checked, see below code snippet:

```
Data_rigging=[{"Name": str(rigging_point_name),
               "Materal": str(Material sling/grommet),
               "Points": list(points connected to the rigging),
               "RWP": float(rigging weight),
               "Angle_1": float(transvere_angle),
               "Angle_2": float(longitudinal_angle),
               "TRF_ans": str(answer TRF factor)
               "SSF_ans": str(Sling safety factor),
               "SKL": [str(answer skl), int(the sling from the analyes)],
               "SLDF" : str(ans sling load distribution factor),
               "sling":[str(id_number),str(type),float(swl),float(diameter),float(n_parts)],
               "Connection_upper":[str(type),float(diameter),float(swl],
               "Connection_lower":[str(type),float(diameter),float(swl]
               }]

```

#### Tab 4
In tab 4, the values for the crane check are entered

- Which crane lifts the lifting point
- Which hoist lifts the lifting point
- The capacity of the hoist 
- The offlead angle of the hoists 

With the help of the method make_data_cranes the data is stored in the a dictionary see code snippet below:

```
data_crane{str(Crane_name):{"DDF": float(DDF_factor),
                            str(hoist): "Data":[float(Capacity),float(off_lead),float(RW)],
                                        "Points": list(points that are lifted by hoist)}

```

If there are multiple cranes used the, there will be two crane names in the keys of the dictionary data_cran, there is a max of two cranes that can be used. If there are multiple hoist used, there will be a hoist added in the diactionary data_crane[Crane_name], with the right info.

<a name="SKL"></a>

## Skew load factor

### Goal 
According to the DNV standard, rigging equipment has a tolerance of 0.25%, what this means is that the sling/grommet maybe 0.25% shorter or 0.25% longer than the original length. This affects all types of lifts, as the load can end up hanging askew. But on a four-point lift, this can affect the force distribution of the slings. According to the DNV standard, the factor for each sling is equal to 1.25, in reality, this factor depends on several values. Such as the in-service length of the slings, the elasticity modulus, the diameter, and the coordinates of both the lift points and the hook. Therefore, it is necessary to see how different lengths affect the forces in the slings, with an iterative process the skew load factor can be determined in more detail.


### Data input

With the help of the method make_skl_data the data is stored in the following structure, see code snippet below: 

```
Data_skl={"Lift_points": [nx[float(point_x),float(point_y),float(point_z)]],
              "ESlings": [float(Esling1),float(Esling2),float(Esling3],float(Esling4)],
              "Hook_point": [float(Hook_x),float(Hook_y),float(Hook_z],
              "DSlings": [float(Dsling1),float(Dsling2),float(Dsling3],float(Dsling4)],
              "LSlings": [float(Lsling1),float(Lsling2),float(Lsling3],float(Lsling4)]}
```

### Flowchart 
![This is a image](/Images_read_me/Flowchart_skl.jpg)

1. Determine the stiffness constant of the slings 
2. Determine the length of the slings: 
    The length of the slings depends on the in-use length of the slings, and if the slings are longer than the measured length because of the tolerance or are shorter than the measured length. In total there are 16 different combinations possible for the slings length, and the code loops through all of them.
3. Determine the start hook point, because of the different lengths of the slings, the start of the hook point is different from the original. See the next chapter for a detailed explanation of the start of the hook point.
4. Determine the number of slack slings, this is based on the distance between the lift points and the length of the slings with tolerance. 
5. Determine Fx, Fy, and Fz forces in hook, Fx and Fy are equal to zero. The Fz force depends on which iteration the "Loop skew load is"
6. When there are 2 slings tight, this means that the hook is on the diagonal line of those two points. So the forces in the slings/ displacement of the hook can be determined using the 2d stiffness method. When there are 3/4 slings tight, the force in the slings/ displacement of the hook can be solved using the 3d stiffness method.
7. Determine the new position, based on the displacement of the hook that was calculated in the last step
8. Determine the total force in slings/ hook, based on the force in slings that was calculated in the last step
9. Checking if "Loop skew" has done all its steps, if this is the case the total force in the z-direction is equal to the total force of the lifting object. If it is not the case, steps 3,4,5,6,7, and 8 are done again, unit all steps have been completed.
10. Store all the results in a dictionary
11. Checking if "Loop options short/long slings" had done all its 16 different combinations, if this is not the case steps 3 t/m 10 will be done again.
12. Determine the max skew load factor of each sling. Also, determine what the displacement of the hook/force in slings was with the max skew load factor and store these in a CSV file

The calculatinos to determine what the force in the slings are and the displacment of the hook are described in more detail in: Matrix Analysis of structure, second edition
### Determine start hook point 
Because of the different lengths, the start of the hook point is different than the original hook point.  See below the flowchart, there has been an assumption made that the slings can not have any strain( no forces), when the forces in the hook are not equal to zero. This is the case when there is one rope tight, and the rope is not directly under the hook. The second case is when there are two tight and the hook lays not on the diagonal of the two liftings points.
![This is a image](/Images_read_me/Flowchart_start_hook_point.jpg)

1. Determine the z-positon of the hook, this point is the first point when a cable is tight, it is determined with the following code, see code snippet below: 
```
    z_hook = []
    for i in range(4):
        # Determine distance between x and y points
        x_dist = Lifting_points[i][0]-Hook_point[0]
        y_dist = Lifting_points[i][1]-Hook_point[1]
        # Z distance between lift point and hook point:
        z_dist = side_3d_line(Lslings[i], x_dist, y_dist)
        # Z_hook height:
        Z_hook_height = z_dist+Lifting_points[i][2]
        z_hook.append(Z_hook_height)
    Hook_point[2] = min(z_hook)+0.000001
```
2. Determine the number of slack slings
3. If there are 3 slack slings, the hook will move to the lifting point of the tight sling, until the hook is right above the lifting point. 
    - First determine the x an y differnce between hook point and hook point(when hook is above lift point)
    - Move the hook in very small steps to the end hook point
    - Determine z-position hook( so that the length of the slings is constant)
    - Determine the number of slack slings
    - when there is no change in the number of slack slings, move do the loop again, otherwise go further in the flowchart.
4. When there are two slings tight, the hook will move to the diagonal line of those two lifting points:
    - First determine the length of the radius line, which the hook will follow, so that both the slings will have a constant length
    - Determine the x,y,z coordinates of the intersection point with the radius line and the diagonal line 
    - Determine the hook with the vertical and the radius line. 
    - Change the hook of the radius line with the vertical in small steps until the radius line is perpendicular to the diagonal line.
    - Check the number of slack slings
    - If there are number of slack slings is not changed and the radius line is perpendicular to the diagonal line, the hook lays on the diagonal line and it is two point lift
    - If there is one or two slack pulled tight it is a 3/ 4 points lift



## Recommendations
When there are made many more extensions to the app and the app gets slow it is recommended to change the structure of the app in such a way that when a parameters is changed not all calculations in the communcation class have to be done. For now the app is still fast enough so it is not necessary to change the structure of the app.