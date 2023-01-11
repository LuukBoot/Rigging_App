
import math
import numpy as np
from numpy.linalg import inv
from .parametrization import Fact_text, Fact_values
import sympy as sym
import json 
import pandas as pd
from pathlib import Path 

# Determine pathfile to skl answer document
Results_SKL = Path(__file__).parent
Results_SKL_File_Path = Results_SKL.parent / "Data_output/Results_SKL.csv"

pi = 3.14159265359


# intersection function
def isect_line_plane_v3(p0, p1, p_co, p_no, epsilon=1e-6):

    """
    p0, p1: Define the line.
    p_co, p_no: define the plane:
        p_co Is a point on the plane (plane coordinate).
        p_no Is a normal vector defining the plane direction;
             (does not need to be normalized).

    Return a Vector or None (when the intersection can't be found).
    """
    # ----------------------
    # generic math functions

    def add_v3v3(v0, v1):
        return (
            v0[0] + v1[0],
            v0[1] + v1[1],
            v0[2] + v1[2],
        )

    def sub_v3v3(v0, v1):
        return (
            v0[0] - v1[0],
            v0[1] - v1[1],
            v0[2] - v1[2],
        )

    def dot_v3v3(v0, v1):
        return (
            (v0[0] * v1[0]) +
            (v0[1] * v1[1]) +
            (v0[2] * v1[2])
        )

    def len_squared_v3(v0):
        return dot_v3v3(v0, v0)

    def mul_v3_fl(v0, f):
        return (
            v0[0] * f,
            v0[1] * f,
            v0[2] * f,
        )

    u = sub_v3v3(p1, p0)
    dot = dot_v3v3(p_no, u)

    if abs(dot) > epsilon:
        # The factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # Otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        w = sub_v3v3(p0, p_co)
        fac = -dot_v3v3(p_no, w) / dot
        u = mul_v3_fl(u, fac)
        return add_v3v3(p0, u)

    # The segment is parallel to plane.
    return None


def acos_degrees(angles):
    """_summary_
    This function returns the degrees of the acos

    Args:
        angles (list(float)): list of angles 

    Returns:
        return angels in degrees 
    """
    angles_degrees = []
    for angle in angles:
        angle_cos = math.acos(angle)
        angles_degrees.append(math.degrees(angle_cos))
    return angles_degrees


def intersection_point_perpendicular(line1, point1):
    """_summary_
    This function descripes the intersection point between a line segment
    (line1), and a perpendicular line
    going through a point(point1).
    source:https://math.stackexchange.com/questions/2325248/find-the-point-of-intersection-between-a-line-segment-ac-and-a-perpendicular-l
    see: for explanation

    Args:
        line1(array[1:2]):      line1[0]=a
                                line1[1]=b
                                y=ax+b

        point2(array[1:2]]):    point2[0]=x
                                point2[1]=y
                                point2(x,y)

    Returns:
        point(array[0:1])":     point[0]=x-coardinate intersection point
                                point[1]=y-coardinate intersection point
                                point[x,y]

    Notes:
    When the slope constant is equal to 0, there will be a small number
    added to the slope constant so there will be no error in calculating the
    slope constant of the perpendicular
    """
    point = [0, 0]
    line2 = [0, 0]
    if line1[0] == 0:
        line1[0] = line1[0]+0.000001
    line2[0] = -1/line1[0]

    line2[1] = point1[1]-line2[0]*point1[0]
    point[0] = (line2[1]-line1[1])/(line1[0]-line2[0])
    point[1] = line1[0]*point[0]+line1[1]

    return point


def side_3d_line(lenght_line, side1, side2):
    """_summary_
    This function calculates the distance of one side of a 3d line
    Args:
        lenght_line (float): length 3d line[mm]
        side1 (float): length side1[mm]
        side2 (float): length side2[mm]
    return:
        side3 (float): length side3[mm]
    """
    
    return math.sqrt(lenght_line**2-side1**2-side2**2)


def distance_points_2d(point1, point2):
    """_summary_
    This function descripes the distance between two points in 2d(only x and y
    coardinates are used )


    Args:
        point1(array[1x2]): point1[0]=x-coardinate point 1(x1)
                            point1[1]=y-coardinate point 1(y1)                    
        point2(array[1x2]): point2[0]=x-coardinate point 2(x2)
                            point2[1]=y-coardinate point 2(y2)
    Returns:
        distance(float):((x1-x2)^2+(y1-y2)^2)^0.5
    """
    distance = math.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)
    return distance


def distance_points_3d(point1, point2):
    """_summary_
    This function descripes the distance between two points in 3d

    Args:
        point1(array[1x3]): point1[0]=x-coardinate point 1(x1)
                            point1[1]=y-coardinate point 1(y1)
                            point1[2]=z-coardinate point 1(z1)
                            
        point1(array[1x3]): point2[0]=x-coardinate point 2(x2)
                            point2[1]=y-coardinate point 2(y2)
                            point2[2]=z-coardinate point 2(z3)

    Returns:
        distance(float):((x1-x2)^2+(y1-y2)^2+(z1-z2)^2)^0.5
    """
    x1 = point1[0]
    y1 = point1[1]
    z1 = point1[2]
    x2 = point2[0]
    y2 = point2[1]
    z2 = point2[2]
    distance = math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    return distance


def slack_slings(Lifting_points, Hook_point, Length_slings):
    """_summary_
    This function descipes which slings are slack this will be done follwing
    these steps:
    Step1: Calculating distance between Hook_point and Lift_points
    Step2: Checking if distance>lengte slings
    Step3:  Yes: Rope is not slack value==1
            No: Rope is slack value==0
    Args:
        Lift_points (array[4x3]):   Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)

                                    Lift_points[1][0]=x-coardinate point 2(x1)
                                    Lift_points[1][1]=y-coardinate point 2(y1)
                                    Lift_points[1][2]=z-coardinate point 2(z1)
                                    etc.

        Hook_point (array[1x3]):    Hook_point[0]=x-coardinate hook point
                                    Hook_point[1]=y-coardinate hook point
                                    Hook_point[2]=z-coardinate hook point

        Length_slings (array[1x4]): Length_slings[0]= Length slings 1
                                    Length_slings[1]= Length slings 2
                                    etc.                                  
    Returns:
        Slings_slack (array[1x4]):Which ropes are slack(slack==0, not slack==1)
    """
    Slings_slack = [0, 0, 0, 0]
    for i in range(4):
        Distance = distance_points_3d(Lifting_points[i], Hook_point)
        if Distance > Length_slings[i]:
            # SLing is tight
            Slings_slack[i] = 1
        else:
            # Sling is slack
            Slings_slack[i] = 0

    return Slings_slack


def angle_3d(point1, point2):
    """_summary_
    This function descipes the angles between two 3d points
    step1: Determine distance between the two points
    step2: Determine the angles
    source:source:https://www.kpu.ca/sites/default/files/Faculty%20of%20Science%20%26%20Horticulture/Physics/Ch2-%202%20-%203DVectors.pdf
    Args:
        point1(array[1x3]): point1[0]=x-coardinate point 1(x1) [mm]
                            point1[1]=y-coardinate point 1(y1) [mm]
                            point1[2]=z-coardinate point 1(z1) [mm]                     
        point1(array[1x3]): point2[0]=x-coardinate point 2(x2) [mm]
                            point2[1]=y-coardinate point 2(y2) [mm]
                            point2[2]=z-coardinate point 2(z3) [mm]
    Returns:
        angles(array[1x3]): angles[0]=angle a[-]
                            angles[1]=angle b[-]
                            angles[2]=angle y-]
    """

    Distance_between_points = distance_points_3d(point1, point2)
    angle_cos_a = ((point1[0]-point2[0])/Distance_between_points)
    angle_cos_b = ((point1[1]-point2[1])/Distance_between_points)
    angle_cos_c = ((point1[2]-point2[2])/Distance_between_points)

    return [angle_cos_a, angle_cos_b, angle_cos_c]


def line_2d(point1, point2):
    """_summary_
    This function caculates the slope constant(a) and starting number(b) from 
    two points
    Args:
        point1(array[1x2]): point1[0]=x-coardinate point 1(x1)
                            point1[1]=y-coardinate point 1(y1)                     
        point2(array[1x2]): point2[0]=x-coardinate point 2(x2)
                            point2[1]=y-coardinate point 2(y2)
    Returns:
        line(array[1x2]):   line[0]=a(the slope constant)
                            line[1]=b(the starting number)
    Note:
        When devided by zero it is assumed that it will be a very large number
    """
    if point1[0]-point2[0] == 0:
        a = (point1[1]-point2[1])/0.000000000000000001
    else:
        a = (point1[1]-point2[1])/(point1[0]-point2[0])
    b = point1[1]-point1[0]*a
    return [a, b]


def distance_line_point(point1_line, point2_line, point3):
    """_summary_
    This functions takes in two points that are on the same line, the function
    calculates the distance between the line and the point:
    Step1: Calculate the line:  Ax+By+C=0
                                where:  A=(y1 - y2)
                                        B=(x2 - x1)
                                        C=(x1y2 - x2y1)
                                source:https://bobobobo.wordpress.com/2008/01/07/solving-linear-equations-ax-by-c-0/                         
    Step2: Calculate the distance between line and point
    Args:
        point1_line(array[1x2]):    point1[0]=x-coardinate point 1 on line(x1)
                                    point1[1]=y-coardinate point 1 on line(y1)         
        point2_line(array[1x2]):    point2[0]=x-coardinate point 2 on line(x2)
                                    point2[1]=y-coardinate point 2 on line(y2)

        point3(array[1x2]):         point3[0]=x-coardinate point3(x3)
                                    point3[1]=y-coardinate point3(y3)                                                   
        formule line:(y1 - y2)x + (x2 - x1)y + (x1y2 - x2y1) = 0
        formule distance point:abs(A*x+B*y)/(A^2+B^2)^0.5

    Returns:
        distance(float): Formula=(abs(A*x+B*y+C))/(A^2+B^2)^0.5

    """

    A = (point1_line[1]-point2_line[1])
    B = (point2_line[0]-point1_line[0])
    C = (point1_line[0]*point2_line[1]-point2_line[0]*point1_line[1])

    return (abs(point3[0]*A+point3[1]*B+C)/(math.sqrt(A**2+B**2)))


def determine_side_pyt_long(side1, side2):
    """_summary_
    This function calculates the long side of a triangle

    Args:
        side1 (float): length side1[mm]
        side2 (float): length side2[mm]

    Returns:
        length(float): (side1^2+side2^2)^0.5
    """
    return math.sqrt(side1**2+side2**2)


def determine_side_pyt_short(long_side, short_side):
    """_summary_
    This function calculates the short side of a triangle

    Args:
        long_side (float): length long side[mm]
        short_side (float): length short[mm]

    Returns:
        length(float): (long_side^2-short_side^2)^0.5
    """
    return math.sqrt(long_side**2-short_side**2)


def Calc_plane1_two_slings_tight(Lifting_points, Point_hook):
    """_summary_
    Het volgt een stappenplan wat uitgeled is in bijlage ..
    Het stuurt de intersectie punt met de diagonaal lijn terug in 
    3d coaardinaten

    Args:
        Lifting_points (array[2x3]): Lift_point[0][0]=x-coardinate punt 1 [mm]
                                    Lift_point[0][1]=y-coardinate punt 1 [mm]
                                    Lift_point[0][2]=z-coardinate punt 1 [mm]

                                    Lift_point[1][0]=x-coardinate punt 2 [mm]
                                    Lift_point[1][1]=y-coardinate punt 2 [mm]
                                    Lift_point[1][2]=z-coardinate punt 2 [mm]

        Point_hook (array[1x3]):    Point_hook[0]=x-coardinate punt haak [mm]
                                    Point_hook[1]=y-coardinate punt haak [mm]
                                    Point_hook[2]=z-coardinate punt haak [mm]

    Returns:
        intersection_point(array[1x3]): intersection_point[0]=x-coardinate
                                        intersectie punt [mm]
                                        intersection_point[1]=y-coardinate 
                                        intersectie punt [mm]
                                        intersection_point[2]=z-coardinate 
                                        intersectie punt [mm]

        Length_radius_line(float):      Length of radius line[mm]

        angle_z_axes_hook_end(float):   max angle z-hook[deg]

    """

    # Step 1 deteremine lengt sides triangle in plane 1
    side_a = distance_points_3d(Lifting_points[0], Lifting_points[1])
    Lsling1 = distance_points_3d(Point_hook, Lifting_points[0])
    Lsling2 = distance_points_3d(Point_hook, Lifting_points[1])

    # stap 2 Determine angles plane 1 with cosinus rule
    angle_alpha_vlak1 = math.acos((Lsling2**2-side_a**2-Lsling1**2) /
                                  (-2*side_a*Lsling1)
                                  )

    # step 3 Determine length radius line
    Length_radius_line = Lsling1*math.sin(angle_alpha_vlak1)
    
    # Step 4: Determine distance between intersection point and lift pointing 
    # point 1 vlak 1
    Distance_1 = Lsling1*math.cos(angle_alpha_vlak1)
    
    # Step 5: Determine angles diagonal line:
    angle_dia_line = angle_3d(Lifting_points[1], Lifting_points[0])

    intersection_point = [0, 0, 0]
    intersection_point[0] = Lifting_points[0][0]+angle_dia_line[0]*Distance_1
    intersection_point[1] = Lifting_points[0][1]+angle_dia_line[1]*Distance_1
    intersection_point[2] = Lifting_points[0][2]+angle_dia_line[2]*Distance_1

    # Stap 5: 
    # Bepalen tot welke hoek met de z-as de radius lijn maximaal gaat
    angle_z_radius_line = abs(90-math.degrees(math.acos(angle_dia_line[2])))

    return [intersection_point, Length_radius_line, angle_z_radius_line]


# Non linear eqatuion solver moet nog worden gerievewed
def nonlinear_equation_solver(
        lift_points, Hook_point, intersection_point, 
        constant_line, angle_z_axes):
    # Determine constant length of slings
    Lsling1 = distance_points_3d(lift_points[0], Hook_point)
    Lsling2 = distance_points_3d(lift_points[1], Hook_point)

    # Determine z-coardinaat hook point:
    z_dist = math.cos(math.radians(angle_z_axes))*constant_line
    Hook_point[2] = intersection_point[2]+z_dist
    
    # Determine 3d angles of slings
    angles_line1 = angle_3d(lift_points[0], Hook_point)
    angles_line2 = angle_3d(lift_points[1], Hook_point)  

    # Determine constant of the equations
    Constant_eq1 = Lsling1**2-(Hook_point[2]-lift_points[0][2])**2
    Constant_eq2 = Lsling2**2-(Hook_point[2]-lift_points[1][2])**2
    
    # Non linear solver
    x, y = sym.symbols("x,y")
    f = sym.Eq((x-lift_points[0][0])**2+(y-lift_points[0][1])**2, Constant_eq1)
    g = sym.Eq((x-lift_points[1][0])**2+(y-lift_points[1][1])**2, Constant_eq2)
    answers = sym.solve([f, g], (x, y))
    
    # Determine which answers it is from the two two answers
    verschil_totaal = [[], []]
    for points in answers:
        Hook_point[0] = points[0]
        Hook_point[1] = points[1]
        # Determine the 3d angles of the lines
        angles_line1_new_point = angle_3d(lift_points[0], Hook_point)
        angles_line2_new_point = angle_3d(lift_points[1], Hook_point)

        verschil1 = 0
        verschil2 = 0
        for i in range(3):
            # Adding the total verschil
            verschil1 = verschil1+(angles_line1_new_point[i]-angles_line1[i])
            verschil2 = verschil2+(angles_line2_new_point[i]-angles_line2[i])
        verschil_totaal[0].append(abs(verschil1))
        verschil_totaal[1].append(abs(verschil2))
    # Determine which answers has the least differnce with the line
    min_value1 = min(verschil_totaal[0])
    min_index = verschil_totaal[0].index(min_value1)
    
    Hook_point[0] = float(answers[min_index][0])
    Hook_point[1] = float(answers[min_index][1])

    Lsling1 = distance_points_3d(lift_points[0], Hook_point)
    Lsling2 = distance_points_3d(lift_points[1], Hook_point)

    # print("DIt is hook point bij output lin solver " +str(Hook_point))

    return [Hook_point, Lsling1, Lsling2]


def determine_height_hook_start(Lslings, Hook_point, Lifting_points):
    """_summary_
    This function determines the height hook start. The z-positions 
    is determined for all four the lifting points with their slings lengths
    the minium hook is the start hook height.

    Args:
        Length_slings ([1x4]array): The length of the 4 slings in array[mm]
        Hook_point (array[1x3]):    Hook_point[0]=x-coardinate hook point
                                    Hook_point[1]=y-coardinate hook point
                                    Hook_point[2]=z-coardinate hook point
        Lift_points (array[4x3]):   Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)
                                    Lift_points[1][0]=x-coardinate point 2(x2)
                                    Lift_points[1][1]=y-coardinate point 2(y2)
                                    Lift_points[1][2]=z-coardinate point 2(z2)
                                    etc.
    Returns:
        Float: Start hook coardinaat z[mm]
    Note:
        When the min hook height is determined it will be added 
        with a small number so that in function slack slings, at least
        one sling is not slack
    """
    
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
    # Determine the minimal hook height
    Hook_point[2] = min(z_hook)+0.000001

    return Hook_point


def Determine_start_hook_point(Lift_points, Hook_point, Length_slings):
    """_summary_
    This function desribes which slings are lifting and which are slack:
    See for more detailed explanation and flowchart:Bijlage II
    See for flowchart of this function Diagrams.md diagram 1

    Args:
        Lift_points (array[4x3]):   Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)

                                    Lift_points[1][0]=x-coardinate point 2(x1)
                                    Lift_points[1][1]=y-coardinate point 2(y1)
                                    Lift_points[1][2]=z-coardinate point 2(z1)
                                    etc.

        Hook_point (array[1x3]):    Hook_point[0]=x-coardinate hook point
                                    Hook_point[1]=y-coardinate hook point
                                    Hook_point[2]=z-coardinate hook point

        Length_slings (array[1x4]): Length_slings[0]= Length slings 1
                                    Length_slings[1]= Length slings 2
                                    etc.

    Returns:
        _Slings_slack(array[1x4]): Which ropes are slack(slack==0,not slack==1)
        Hook_point (array[1x3]):    Hook_point[0]=x-coardinate hook point
                                    Hook_point[1]=y-coardinate hook point
                                    Hook_point[2]=z-coardinate hook point

    """

    # The steps the calculation needs to loop through
    steps_3_slack = 10000  # For calculation with 3 slings slack     
    steps_2_slack = 1000  # For calculation with 2 slings slack

    # Determine z-position hook
    Hook_point = determine_height_hook_start(Length_slings, 
                                             Hook_point, 
                                             Lift_points)
    # Determine number of slack slings: 
    _Slings_slack = slack_slings(Lift_points, Hook_point, Length_slings)
    N_slings_slack = _Slings_slack.count(0)

    # 3 slack slings
    if N_slings_slack == 3:
        for i in range(4):
            # Determine which of the four slings is not slack
            if _Slings_slack[i] == 1: 
                # Lifting point/length sling of tight sling
                Lift_point_tight = Lift_points[i]   
                Lsling_tight = distance_points_3d(Lift_point_tight, Hook_point)
        # Vector hook
        delta_hook_x = (Lift_point_tight[0]-Hook_point[0])*(1/steps_3_slack)
        delta_hook_y = (Lift_point_tight[1]-Hook_point[1])*(1/steps_3_slack)
        # Loop one tight sling
        i = 0
        while i < steps_3_slack and N_slings_slack == 3:
            # Determine x and y coardinates hook
            Hook_point[0] = Hook_point[0]+delta_hook_x
            Hook_point[1] = Hook_point[1]+delta_hook_y
            # Determine x/y and z distance between points
            x_dist = Hook_point[0]-Lift_point_tight[0]
            y_dist = Hook_point[1]-Lift_point_tight[1]
            z_dist = side_3d_line(Lsling_tight, x_dist, y_dist)
            # Determine z coordinaat hook point 
            Hook_point[2] = z_dist+Lift_point_tight[2]+0.00000001
            # Determine number of slack slings: 
            _Slings_slack = slack_slings(Lift_points, Hook_point, 
                                         Length_slings)
            N_slings_slack = _Slings_slack.count(0)

    # Two slack slings
    if N_slings_slack == 2:
        Lift_points_tight = [[], []]  # Lifting points with a tigth sling 
        
        j = 0
        # Determine the slings that are tight 
        for i in range(4): 
            if _Slings_slack[i] == 1:
                Lift_points_tight[j] = Lift_points[i]
                j = j+1
        # Calculations plane 1
        _results = Calc_plane1_two_slings_tight(Lift_points_tight, Hook_point)
        inter_section_point = _results[0]
        Lenght_radius_line = _results[1]
        min_angle_z_radius_line = _results[2]
        
        # Determine the angle with the z-axes of the radiusl ine
        angles_radius_line = angle_3d(Hook_point, inter_section_point)
        z_angle_start = math.degrees(math.acos(angles_radius_line[2]))

        # make a list with angles to loop through
        angles_list = np.linspace(z_angle_start,
                                  min_angle_z_radius_line, 
                                  steps_2_slack)
        # Check if the angles are not equal to each other
        if abs(z_angle_start-min_angle_z_radius_line) > 0.001:
            i = 0
            # Loop 2 slings slack
            while i < steps_2_slack and N_slings_slack > 1:
                # Determine hook_point with the function
                Hook_point = nonlinear_equation_solver(Lift_points_tight, 
                                                       Hook_point,
                                                       inter_section_point,
                                                       Lenght_radius_line,
                                                       angles_list[i])[0]
                # Determine number of slack slings: 
                _Slings_slack = slack_slings(Lift_points,
                                             Hook_point,
                                             Length_slings)
                N_slings_slack = _Slings_slack.count(0)
                i += 1

    """print("Return start hook point")
    print("Deze slings zijn strak: "+
    str(slack_slings(Lift_points,Hook_point,Length_slings)))
    print("Dit is de lengte van sling 1: " 
    +str(distance_points_3d(Lift_points[0],Hook_point))
     +" Voor de loop: " +str(Length_slings[0]))
    print("Dit is de lengte van sling 2: " +
    str(distance_points_3d(Lift_points[1],Hook_point)) +" Voor de loop: " +
    str(Length_slings[1]))
    print("Dit is de lengte van sling 3: " +
    str(distance_points_3d(Lift_points[2],Hook_point)) +" Voor de loop: " +
    str(Length_slings[2]))
    print("Dit is de lengte van sling 4: " +
    str(distance_points_3d(Lift_points[3],Hook_point)) +" Voor de loop: " +
    str(Length_slings[3]))"""
    Hook_point[0] = float(Hook_point[0])
    Hook_point[1] = float(Hook_point[1])
    Hook_point[2] = float(Hook_point[2])
    return Hook_point


def average(lst):
    return sum(lst)/len(lst)


def stifness_ratio(A, E, L):
    """_summary_
    This function calculates the stifness ratio a a beam

    Args:
        A (Float): Area [mm^2]
        E (Float): Elastic modulus [N/mm^2]
        L (Float): length beam [mm]
    Returns:
        k (float): (E*A)/L [N/mm]
    """
    return ((E*A)/L)


def local_stifness_matrix_3d(angles, k):
    """_summary_
    Calculates the local stifness matrix of a 3d truss the matrix will be [6x6]
    source:https://www.youtube.com/watch?v=traRrnfryxE&t=603s&ab_channel=juanpaulobersamina
    minute:10.05



    Args:
        angles (array[1x3]):    angles[0]=angle_a[-]
                                angles[1]=angle_b[-]
                                angles[1]=angle_y[-]

        k (float):              Stifness ratio[N/mm]

    Returns:
        k2(matrix[3x3]): Stifness matrix side B
    
    Note:
        This function only returns the stifness matrix side B, because side B
        is only used
        for the global matrix(see for futher information document......)
    """
    f11 = angles[0]**2
    f12 = angles[0]*angles[1]
    f13 = angles[0]*angles[2]
    # f14 = -f11
    # f15 = -f12
    # f16 = -f13
    f22 = (angles[1])**2
    f23 = angles[1]*angles[2]
    # f24 = -f12
    # f25 = -f22
    # f26 = -f23
    f33 = angles[2]**2
    # f34 = -f13
    # f35 = -f23
    # f36 = -f33
    f44 = f11
    f45 = f12
    f46 = f13
    f55 = f22
    f56 = f23
    f66 = f33
    """
    k1=k*np.array([[f11,f12,f13,f14,f15,f16],
                    [f12,f22,f23,f24,f25,f26],
                    [f13,f23,f33,f34,f35,f36],
                    [f14,f24,f34,f44,f45,f46],
                    [f15,f25,f35,f45,f55,f56],
                    [f16,f26,f36,f46,f56,f66]])"""               
    k2 = k*np.array([[f44, f45, f46],
                     [f45, f55, f56],
                     [f46, f56, f66]])
    return k2 


def vector_1(Values):
    """_summary_
    This function makes vector of nx1
    Wordt gebruikt om vectors van nx1 length te maken

    Args:
        Values= Which values needs to be transformed into a nx1 matrix
    """

    array = np.zeros((len(Values), 1))
    
    for i in range(len(Values)):
        array[i][0] = Values[i]
    return array


def translation_matrix_3d(angles):
    """_summary_
    This function makes the translation matrix of 3d truss
    source:https://repository.bakrie.ac.id/10/1/%5BTSI-LIB-131%5D%5BAslam_Kassimali%5D_Matrix_Analysis_of_Structure.pdf
    equation: From source it is equation 8.6

    Args:
        angles (array[1x3]):    angles[0]=angle_a[-]
                                angles[1]=angle_b[-]
                                angles[1]=angle_y[-]

    Returns:
        T_matrix(matrix[2x6]):
    """

    T_matrix = np.array([[angles[0], angles[1], angles[2], 0, 0, 0],
                         [0, 0, 0, angles[0], angles[1], angles[2]]])
    return T_matrix


def translation_matrix_2d(angle):
    """_summary_
    This function describe how to make the translation matrix for a 2d problem 
    source:https://repository.bakrie.ac.id/10/1/%5BTSI-LIB-131%5D%5BAslam_Kassimali%5D_Matrix_Analysis_of_Structure.pdf
    equation: 3.59

    Args:
        angle (flaot):angle of sling[deg]

    Returns:
        T_matrix(matrix[4x4])
    """
    cos_a = math.cos(math.radians(angle))
    sin_a = math.sin(math.radians(angle))

    T_matrix = np.array([[cos_a, sin_a, 0, 0],
                         [-sin_a, cos_a, 0, 0],
                         [0, 0, cos_a, sin_a],
                         [0, 0, -sin_a, cos_a]])
    return T_matrix


def stifness_matrix(k):
    """_summary_
    This function makes a 2x2 stifness matrix
    source:https://repository.bakrie.ac.id/10/1/%5BTSI-LIB-131%5D%5BAslam_Kassimali%5D_Matrix_Analysis_of_Structure.pdf
    equation: From source it is equation 8.3

    Args:
        k (float): stifness ratio[N/mm]

    Returns:
        stifness matrix[2x2]
    """
    return np.array([[k, -k],
                     [-k, k]])


def stifness_matrix_2d(k):
    """_summary_
    This function makes a 4x4 stifness matrix
    source:https://repository.bakrie.ac.id/10/1/%5BTSI-LIB-131%5D%5BAslam_Kassimali%5D_Matrix_Analysis_of_Structure.pdf
    equation: From source it is equation 3.27

    Args:
        k (float): stifness ratio[N/mm]

    Returns:
        stifness matrix[4x4]
    """
    k = np.array([[k, 0, -k, 0],
                  [0, 0, 0, 0],
                  [-k, 0, k, 0],
                  [0, 0, 0, 0]])
    return k


def force_displacement_3d(Lift_points, Hook_point, k, F):
    """_summary_
    This function desrives the force calculation/ displacement of a 3d truss, 
    where side  a of the elements is equal to the lifting point and all 
    side b of the  elements are connected to one point on the hook

    It is possible to have 3 elements connected to the hook or 4
    source:https://repository.bakrie.ac.id/10/1/%5BTSI-LIB-131%5D%5BAslam_Kassimali%5D_Matrix_Analysis_of_Structure.pdf
    Chapter 8


    Args:
        Lift_points (array[4/3x3]): Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)

                                    Lift_points[1][0]=x-coardinate point 2(x1)
                                    Lift_points[1][1]=y-coardinate point 2(y1)
                                    Lift_points[1][2]=z-coardinate point 2(z1)
                                    etc.

        Hook_point (array[1x3]):    Hook_point[0]=x-coardinate hook point
                                    Hook_point[1]=y-coardinate hook point
                                    Hook_point[2]=z-coardinate hook point
        k (float): _description_
        F ([1x3]array): F[0]= Force in x-direction[N]
                        F[1]= Force in y-direction[N]
                        F[2]= Force in z-direction[N]

    Returns:
        delta_hook([1x3]array): delta_hook[0]= x-Displacement hook[mm]
                                delta_hook[1]= y-Displacement hook[mm]
                                delta_hook[2]= z-Displacement hook[mm]  
        F_sling(array[3/4x1]): Force slings[N]

    """
    # Determine the force matrix [3x1]
    Force_matrix = vector_1(F)
    # Makin [3x3] matrix
    Matrix_s = np.zeros((3, 3))

    Rek = []  # List for strain
    F_sling = []  # List for force in slings
    Rek_sling = []  # List for strain slings
    Translation_matrix = []  # Making list for all translation matrix
    i = 0
    for point in Lift_points:
        angles = angle_3d(Hook_point, point)
        Translation_matrix.append(translation_matrix_3d(angles))
        matrix = local_stifness_matrix_3d(angles, k[i])
        # Determine stucture stifness matrix
        Matrix_s = np.add(Matrix_s, matrix)
        i = i+1
    # Determine local displacement see eq 8.2
    displacement = np.matmul(inv(Matrix_s), Force_matrix)
    # Determine hook displacement
    delta_hook = [displacement[0][0], displacement[1][0], displacement[2][0]]
    # Determine displacement vector side a is equal to zero, because lifting
    # point is not moving and side b is equal to the displament of the hook
    total_displacement_vector = vector_1([0,
                                          0,
                                          0,
                                          delta_hook[0],
                                          delta_hook[1],
                                          delta_hook[2]])

    for i in range(len(Lift_points)):
        # Determine local strain elements see eq 8.7
        Rek = np.matmul(Translation_matrix[i], total_displacement_vector)
        Rek_sling.append(Rek[1][0])
        # Determine force in elements see eq 8.10
        _F_sling = np.matmul(stifness_matrix(k[i]), Rek)
        F_sling.append(_F_sling[1][0])
    
    return [delta_hook, F_sling, Rek_sling]


def local_stifness_matrix_2d(angle, k):
    """_summary_
    stifness matrix 2d(see engineersmodel for answer)
    Args:
        angles (float): angle[deg]
        k (float): stifness of beam[N/mm]
    """
    cos_a = math.cos(math.radians(angle))
    sin_a = math.sin(math.radians(angle))
    f11 = cos_a**2
    f12 = cos_a*sin_a
    # f13 = -f11
    # f14=-f12
    f22 = sin_a**2
    # f23 = f13
    # f24=-f22
    f33 = f11
    f34 = f12
    f44 = f22

    """    
    k1=k*np.array([[f11,f12,f13,f14],
                    [f12,f22,f23,f24],
                    [f13,f23,f33,f34],
                    [f14,f24,f34,f44]])"""
    k2 = k*np.array([[f33, f34],
                    [f34, f44]])

    return k2


def force_displacement_2d(Lift_points, Hook_point, k, F):
    """_summary_
    This function desrives the force calculation/ displacement of a 2d truss, 
    where side  a of the elements is equal to the lifting point and side B
    of the elemenents are connected to the hook

    
    source:https://repository.bakrie.ac.id/10/1/%5BTSI-LIB-131%5D%5BAslam_Kassimali%5D_Matrix_Analysis_of_Structure.pdf
    Chapter 3


    Args:
        Lift_points (array[2x3]): Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)

                                    Lift_points[1][0]=x-coardinate point 2(x1)
                                    Lift_points[1][1]=y-coardinate point 2(y1)
                                    Lift_points[1][2]=z-coardinate point 2(z1)
                                  

        Hook_point (array[1x3]):    Hook_point[0]=x-coardinate hook point
                                    Hook_point[1]=y-coardinate hook point
                                    Hook_point[2]=z-coardinate hook point
        k (float): (array[2x1]):    k[0]= Stifness ratio element 1[N/mm^2]
                                    k[1]= Stifness ratio element 2[N/mm^2]
        F ([1x3]array): F[0]= Force in x-direction[N]
                        F[1]= Force in z-direction[N]
                        

    Returns:
        delta_hook([1x3]array): delta_hook[0]= x-Displacement hook[mm]
                                delta_hook[1]= y-Displacement hook[mm]
                                delta_hook[2]= z-Displacement hook[mm]  
        F_sling(array[3/4x1]): Force slings[N]

    """
    # Making list/matrixes
    Rek = []  # List for strain
    F_sling = []  # List for force in slings
    Rek_sling = []  # List for strain slings
    delta_hook = [0, 0, 0]  # list for hook displacement
    Translation_matrix = [[], []]  # Making list for all translation matrix
    Matrix_s = np.zeros((2, 2))   # Makin [3x3] matrix

    # Force matrix from 3d to 2d
    Force_matrix = np.array([[determine_side_pyt_long(F[0], F[1])], [F[2]]])

    diogonaal_line_x_y_plane = line_2d(Lift_points[0], Lift_points[1])
    angle_diogonaal_line_x_y_plane = math.atan(diogonaal_line_x_y_plane[0])

    for i in range(2):
        angle = angle_3d(Lift_points[i], Hook_point)
        # Determine angle in 2d problem
        _angle = math.degrees(math.acos(angle[2]))
        _angle = 90-_angle
        if angle[0] < 0:
            _angle = -_angle
        # Determine translation matrix
        Translation_matrix[i] = translation_matrix_2d(_angle)
        # Determine local matrix
        matrix = local_stifness_matrix_2d(_angle, k[i])
        # Determine stucture stifness matrix
        Matrix_s = np.add(Matrix_s, matrix)

    # Determine displacement hook see eq 3.4
    displacement = np.matmul(inv(Matrix_s), Force_matrix)

    # Transfroming 2d displacement to 3d 
    delta_hook[0] = math.cos(angle_diogonaal_line_x_y_plane)*displacement[0][0]
    delta_hook[1] = math.sin(angle_diogonaal_line_x_y_plane)*displacement[0][0]
    delta_hook[2] = displacement[1][0]
    
    # Determine displacement vector side a is equal to zero, because lifting
    # point is not moving and side b is equal to the displament of the hook
    total_displacement_vector = vector_1([0,
                                          0, 
                                          displacement[0][0], 
                                          delta_hook[2]])

    for i in range(len(Lift_points)):
        # Transformation local to global coardinate system see eq 3.63
        Rek = np.matmul(Translation_matrix[i], total_displacement_vector)
        Rek_sling.append(determine_side_pyt_long(Rek[3][0], Rek[3][0]))
        # Determine force in sling F=k*u
        _F_sling = np.matmul(stifness_matrix_2d(k[i]), Rek)
        F_sling.append(abs(_F_sling[0][0]))

    return [delta_hook, F_sling, Rek_sling]


def determine_load_dis_two_point(pointA, pointB, COG):
    """_summary_
    Determine load distribution of a two point lift 
    

    Args:
        pointA ([1x3]array):pointA[0]= x-coardinate point A[mm]
                            pointA[0]= y-coardinate point A[mm]
                            pointA[0]= z-coardinate point A[mm]
        pointB ([1x3]array):pointB[0]= x-coardinate point B[mm]
                            pointB[0]= y-coardinate point B[mm]
                            pointB[0]= z-coardinate point B[mm]
        COG ([1x3]array):   COG[0]= x-coardinate COG[mm]
                            COG[1]= y-coardinate COG[mm]
                            COG[2]= z-coardinate COG[mm]

    Returns:
        load_dis[[1x2]array]:   load_dis[0]= Point A dis[-]
                                load_dis[1]= Point B dis[-]
    """
    distance_A_cog = distance_points_2d(pointA, COG)
    distance_B_cog = distance_points_2d(pointB, COG)
    distance_A_B = distance_points_2d(pointA, pointB)
    A_proc = distance_B_cog/distance_A_B
    B_proc = distance_A_cog/distance_A_B

    return [A_proc, B_proc]


def determine_load_dis_three_point(pointA, pointB, pointC, COG):
    """_summary_
    Determine load distribution of a three point lift
    Source: https://www.neptuneenergy.com/sites/neptuneenergy-corp/files/operations/supply-chain/MSD-PROJ-AJ-12-00207%20-%20General%20Specification%20207%20-%20Guideline%20for%20Lifting%20Provisions%20for%20Items%20Transported%20on%20a%20Supply%20Vessel_2.pdf
    Chapter: 3 point lift

    Args:
        pointA ([1x3]array):pointA[0]= x-coardinate point A[mm]
                            pointA[0]= y-coardinate point A[mm]
                            pointA[0]= z-coardinate point A[mm]
        pointB ([1x3]array):pointB[0]= x-coardinate point B[mm]
                            pointB[0]= y-coardinate point B[mm]
                            pointB[0]= z-coardinate point B[mm]
        pointC ([1x3]array):pointC[0]= x-coardinate point C[mm]
                            pointC[0]= y-coardinate point C[mm]
                            pointC[0]= z-coardinate point C[mm]
        COG ([1x3]array):   COG[0]= x-coardinate COG[mm]
                            COG[1]= y-coardinate COG[mm]
                            COG[2]= z-coardinate COG[mm]

    Returns:
        load_dis[[1x3]array]:   load_dis[0]= Point A dis[-]
                                load_dis[1]= Point B dis[-]
                                load_dis[2]= Point C dis[-]
    """
    # Determine A_proc
    dis_cog_sideb_c = distance_line_point(pointB, pointC, COG)
    dis_a_sideb_c = distance_line_point(pointB, pointC, pointA)
    A_proc = dis_cog_sideb_c/dis_a_sideb_c
    # Determine B_proc
    dis_cog_sidea_c = distance_line_point(pointA, pointC, COG)
    dis_b_sidea_c = distance_line_point(pointA, pointC, pointB)
    B_proc = dis_cog_sidea_c/dis_b_sidea_c
    # Determine C_proc
    dis_cog_sidea_b = distance_line_point(pointA, pointB, COG)
    dis_c_sidea_b = distance_line_point(pointA, pointB, pointC)
    C_proc = dis_cog_sidea_b/dis_c_sidea_b

    return [A_proc, B_proc, C_proc]


def determine_load_dis_four_point(pointA, pointB, pointC, pointD, COG):
    """_summary_
    Determine load distribution of a three point lift
    Source: https://www.researchgate.net/publication/306000332_Offshore_Heavy_Lift_Design_and_Operations_Sling_Tension_in_Heavy_Lifts_with_Quadruple_Sling_Arrangement
    Chapter: 4.1

    Args:
        pointA ([1x3]array):pointA[0]= x-coardinate point A[mm]
                            pointA[0]= y-coardinate point A[mm]
                            pointA[0]= z-coardinate point A[mm]
        pointB ([1x3]array):pointB[0]= x-coardinate point B[mm]
                            pointB[0]= y-coardinate point B[mm]
                            pointB[0]= z-coardinate point B[mm]
        pointC ([1x3]array):pointC[0]= x-coardinate point C[mm]
                            pointC[0]= y-coardinate point C[mm]
                            pointC[0]= z-coardinate point C[mm]
        pointD ([1x3]array):pointD[0]= x-coardinate point D[mm]
                            pointD[0]= y-coardinate point D[mm]
                            pointD[0]= z-coardinate point D[mm]
        COG ([1x3]array):   COG[0]= x-coardinate COG[mm]
                            COG[1]= y-coardinate COG[mm]
                            COG[2]= z-coardinate COG[mm]

    Returns:
        load_dis[[1x4]array]:   load_dis[0]= Point A dis[-]
                                load_dis[1]= Point B dis[-]
                                load_dis[2]= Point C dis[-]
                                load_dis[3]= Point C dis[-]
    """
    A_proc = (((pointD[1]+pointC[1])/2-COG[1])/((pointD[1]+pointC[1])/2-(pointA[1]+pointB[1])/2))*(((pointB[0]+pointC[0])/2-COG[0])/((pointB[0]+pointC[0])/2-(pointA[0]+pointD[0])/2))
    B_proc = (((pointD[1]+pointC[1])/2-COG[1])/((pointD[1]+pointC[1])/2-(pointA[1]+pointB[1])/2))*((COG[0]-(pointA[0]+pointD[0])/2)/((pointB[0]+pointC[0])/2-(pointA[0]+pointD[0])/2))
    C_proc = ((COG[1]-(pointA[1]+pointB[1])/2)/((pointD[1]+pointC[1])/2-(pointA[1]+pointB[1])/2))*((COG[0]-(pointA[0]+pointD[0])/2)/((pointB[0]+pointC[0])/2-(pointA[0]+pointD[0])/2))
    D_proc = ((COG[1]-(pointA[1]+pointB[1])/2)/((pointD[1]+pointC[1])/2-(pointA[1]+pointB[1])/2))*(((pointB[0]+pointC[0])/2-COG[0])/((pointB[0]+pointC[0])/2-(pointA[0]+pointD[0])/2))

    return [A_proc, B_proc, C_proc, D_proc]


def COG_shift_factor_two_point(Lift_points, COG_envelope):
    """_summary_
    This calcluates the load distribution of a two point lift with all
    possibilities for the cog envelope(8 possibilities)
    Args:
        Lift_points (array[2x3]):   Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)
                                    Lift_points[1][0]=x-coardinate point 2(x2)
                                    Lift_points[1][1]=y-coardinate point 2(y2)
                                    Lift_points[1][2]=z-coardinate point 2(z2)
                                    etc.
        COG_envelope (array[8x2]):  COG[0][0]= x-coardinate COG 1[mm]
                                    COG[0][1]= y-coardinate COG 1[mm]
                                    COG[1][0]= x-coardinate COG 2[mm]
                                    COG[1][1]= y-coardinate COG 2[mm]
                                    etc.

    Returns
        dis_cog_shift(array[2x8]):array[0]= dis_cog_shift[0]= Load dis point A
                                                            for all COG points'
                                            dis_cog_shift[1]= Load dis point B
                                                            for all COG points

    """
    # Making empty lists
    COG_shifts_A = []
    COG_shifts_B = []

    # Loop through 8 cog possibilities
    for point in COG_envelope:
        results_cog_shift = determine_load_dis_two_point(Lift_points[0],
                                                         Lift_points[1], 
                                                         point)
        COG_shifts_A.append(results_cog_shift[0])
        COG_shifts_B.append(results_cog_shift[1])

    return [COG_shifts_A, COG_shifts_B]


def COG_shift_factor_three_point(Lift_points, COG_envelope):
    """_summary_
    This calcluates the load distribution of a three point lift with all
    possibilities for the cog envelope(8 possibilities)
    Args:
        Lift_points (array[3x3]):   Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)
                                    Lift_points[1][0]=x-coardinate point 2(x2)
                                    Lift_points[1][1]=y-coardinate point 2(y2)
                                    Lift_points[1][2]=z-coardinate point 2(z2)
                                    etc.
        COG_envelope (array[8x2]):  COG[0][0]= x-coardinate COG 1[mm]
                                    COG[0][1]= y-coardinate COG 1[mm]
                                    COG[1][0]= x-coardinate COG 2[mm]
                                    COG[1][1]= y-coardinate COG 2[mm]
                                    etc.

    Returns
        dis_cog_shift(array[3x8]):array[0]= dis_cog_shift[0]= Load dis point A
                                                            for all COG points'
                                            dis_cog_shift[1]= Load dis point B
                                                            for all COG points
                                            dis_cog_shift[2]= Load dis point C
                                                            for all COG points
    """
    # Making empty lists
    COG_shifts_A = []
    COG_shifts_B = []
    COG_shifts_C = []

    # Loop through 8 cog possibilities
    for point in COG_envelope:
        results_cog_shift = determine_load_dis_three_point(Lift_points[0], 
                                                           Lift_points[1],
                                                           Lift_points[2],
                                                           point)
        COG_shifts_A.append(results_cog_shift[0])
        COG_shifts_B.append(results_cog_shift[1])
        COG_shifts_C.append(results_cog_shift[2])

    return [COG_shifts_A, COG_shifts_B, COG_shifts_C]


def COG_shift_factor_four_point(Lift_points, COG_envelope):
    """_summary_
    This calcluates the load distribution of a Four point lift with all
    possibilities for the cog envelope(8 possibilities)
    Args:
        Lift_points (array[4x3]):   Lift_points[0][0]=x-coardinate point 1(x1)
                                    Lift_points[0][1]=y-coardinate point 1(y1)
                                    Lift_points[0][2]=z-coardinate point 1(z1)
                                    Lift_points[1][0]=x-coardinate point 2(x2)
                                    Lift_points[1][1]=y-coardinate point 2(y2)
                                    Lift_points[1][2]=z-coardinate point 2(z2)
                                    etc.
        COG_envelope (array[8x2]):  COG[0][0]= x-coardinate COG 1[mm]
                                    COG[0][1]= y-coardinate COG 1[mm]
                                    COG[1][0]= x-coardinate COG 2[mm]
                                    COG[1][1]= y-coardinate COG 2[mm]
                                    etc.

    Returns
        dis_cog_shift(array[4x8]):array[0]= dis_cog_shift[0]= Load dis point A
                                                            for all COG points'
                                            dis_cog_shift[1]= Load dis point B
                                                            for all COG points
                                            dis_cog_shift[2]= Load dis point C
                                                            for all COG points
                                            dis_cog_shift[1]= Load dis point D
                                                            for all COG points
    """
    # Making empty lists
    COG_shifts_A = []
    COG_shifts_B = []
    COG_shifts_C = []
    COG_shifts_D = []

    # Loop through 8 cog possibilities
    for point in COG_envelope:
        results_cog_shift = determine_load_dis_four_point(Lift_points[0],
                                                          Lift_points[1],
                                                          Lift_points[2],
                                                          Lift_points[3],
                                                          point)
        COG_shifts_A.append(results_cog_shift[0])
        COG_shifts_B.append(results_cog_shift[1])
        COG_shifts_C.append(results_cog_shift[2])
        COG_shifts_D.append(results_cog_shift[3])

    return [COG_shifts_A, COG_shifts_B, COG_shifts_C, COG_shifts_D]


def factors_no_calculations(factor, value):
    """_summary_
    This function determines the factor value, and gets
    the values from the constant file

    Returns:
        answer: factor
    """
    answer = Fact_values[factor][value]
    return answer


def daf_factor(weight, answer):
    """_summary_

    Args:
        weight (dict): Form viktor gets dictionary with all weights values
        value (string): Is the lift offshore or inshore
    Note:
        First the number is determined, it is zero if onshore and one 
        if inshore this is
        because the values are stored in a array and offshore on place 0 
        eand inshore on place 
        1
    """
    # Determine if the lift is offshore or inshore
    if answer == "Offshore":
        number = 0
    if answer == "Inshore":
        number = 1  
    # Determine LW weight
    total_weight = weight 

    if 100 < total_weight <= 300:
        texts = "100<W<300"
    if 300 < total_weight <= 1000:
        texts = "300<W<1000"
    if 1000 < total_weight <= 2500:
        texts = "1000<W<2500"
    if 2500 < total_weight <= 10000:
        texts = "2500<W<10000"
    #print(Constants.list_factors_values["DAF"])
    if total_weight > 100:
        daf = Fact_values["DAF"][texts][number]
    else:
        if number == 0:
            # formula DAF factor(offshore) DNV norm (see 16.2.5.6)
            daf = 1+0.25*math.sqrt(100/total_weight)
        if number == 1:
            # formula DAF factor(inshore) DNV norm (see 16.2.5.6)
            daf = 1.07+0.05*math.sqrt(100/total_weight)

    return daf


# hier moet nog meer bij worden gedaan moet nog worden gekeken naar de 
# verschillende toleranties
def determine_length_slings(sling_short, SWL):
    """_summary_
    This function determines the length of slings based on the tolerance of 
    the DNV norm


    Args:
        sling_short [4x1]:  0= Slings is long 
                            1= SLings is short
                            2= Normal length
                        
        SWL ([4x1]): The swl length of the slings
    """

    delta_length_slings = [0, 0, 0, 0]
    length_slings = [0, 0, 0, 0]

    for i in range(4):
        if sling_short[i] == 0:                     
            delta_length_slings[i] = 0.0025*SWL[i]
        if sling_short[i] == 1:
            delta_length_slings[i] = -0.0025*SWL[i]
        if sling_short[i] == 2:
            delta_length_slings[i] = 0

        length_slings[i] = SWL[i]+delta_length_slings[i]

    return [length_slings, delta_length_slings]


# Moet nog een uitleg bij worden gegeven
def determine_angles_object(COG, Hook_point):
    delta_x_cog_hook_point = COG[0]-Hook_point[0]
    delta_y_cog_hook_point = COG[1]-Hook_point[1]

    angle_pitch = math.degrees(math.asin((-delta_x_cog_hook_point)/(COG[2])))
    angle_roll = math.degrees(math.asin((-delta_y_cog_hook_point)/(COG[2])))

    COG[0] = COG[0]+math.sin(math.radians(angle_pitch))*COG[2]
    COG[1] = COG[1]+math.sin(math.radians(angle_roll))*COG[2]

    """print("Check pitch and roll")
    print("Angle pitch: "+ str(angle_pitch)+"deg")
    print("Angle roll: "+ str(angle_roll)+"deg")
    print("Dit is punt COG: "+str(COG))"""

    return [angle_pitch, angle_roll]


class Calc_COG_env:

    def __init__(self, object_values, COG):
        """_summary_
        This function calculates the COG envelope according to the
        DNV paragraph 5.6.2.3 guidance note 1)
            object_values (array[1x3]): object_values[0]= Object length[mm]
                                        object_values[1]= Object width[mm]
                                        object_values[2]= Object height[mm]
                    COG ([1x3]array):   COG[0]= x-coardinate COG[mm]
                                        COG[1]= y-coardinate COG[mm]
                                        COG[2]= z-coardinate COG[mm]
        """
        self.COG_env_size=[object_values[0]*0.05,
                           object_values[1]*0.05,
                           object_values[2]*0.05]
        # Determine delta x and delta y
        Delta_x = self.COG_env_size[0]*0.5  # See DNV is equal to 0.05xlength
        Delta_y = self.COG_env_size[1]*0.5  # See DNV is equal to 0.05xwidth
    
        # COG envelope only x direction
        self.COG_env_x = [[COG[0]+Delta_x, COG[1]],  
                          [COG[0]-Delta_x, COG[1]]]
        # COG envelope only y direction          
        self.COG_env_y = [[COG[0], COG[1]+Delta_y],
                          [COG[0], COG[1]-Delta_y]]
        # COG envelope both direction
        self.COG_env_both = [[COG[0]+Delta_x, COG[1]+Delta_y],
                             [COG[0]-Delta_x, COG[1]-Delta_y],
                             [COG[0]-Delta_x, COG[1]+Delta_y],
                             [COG[0]+Delta_x, COG[1]-Delta_y]]
        # COG envelope total
        self.COG_env_total = self.COG_env_x+self.COG_env_y+self.COG_env_both
    
    @property  
    def get_cog_env_total(self):
        return self.COG_env_total
   
    @property 
    def get_cog_env_x(self):
        return self.COG_env_x
    
    @property
    def get_cog_env_y(self):
        return self.COG_env_y
    
    @property
    def get_cog_env_both(self):
        return self.COG_env_both
    
    @property
    def get_cog_env_size(self):
        return self.COG_env_size

class Calc_SKL:
    def __init__(self, 
                 Data_SKL,
                 Data_general):
        """_summary_
        In this class the max skew load factor is determined, 
        it loops trough all 16 options for the slings short/long

        Args:
            Data_skl(dictanary): Data for calculating SKL
            Data_general(dictanary): Data for calculating general
        
        returns: SKL parameters
        """
        print(Data_SKL)
        print(Data_general)
        

        
        # Share variables with other methods
        self.Hook_point_x = Data_SKL["Hook_point"][0]
        self.Hook_point_y = Data_SKL["Hook_point"][1]
        self.Hook_point_z = Data_SKL["Hook_point"][2]
        self.COG_x = Data_general["COG"][0]
        self.COG_y = Data_general["COG"][1]
        self.COG_z = Data_general["COG"][2]
        self.F_load_total = Data_general["LW"]*1000*9.81
        self.Lift_points = Data_SKL["Lift_points"]
        self.steps = 1000  # Amount of steps that the loop goes through
        self.max_skew_load_factor = [0, 0, 0, 0]

        # Results skew load fac
        Results_skl = []
        # Making lists for al 16 options
        list_loop = {"Length_slings": [],
                     "Short_long_slings": []}
        # Array so it can be easyly detemrined which is the max sling force
        F_slings_list_total = [[], [], [], []]
        self.values_pitch_roll_angles = {"Max roll": None,
                                          "Min roll": None,
                                          "Max pitch": None,
                                          "Min pitch": None}
        # Making dictionary where are all input parametser/ results are put in
        self.Checks_SKL = {"Results_normal_length": None,
                           "SKL_factor":[]}
                           
                            

        # Making a list so that it can loop throug al 16 options
        options_list_slings_short_long = []
        for number1 in range(2):
            for number2 in range(2):
                for number3 in range(2):
                    for number4 in range(2):
                        options_list_slings_short_long.append([number1,
                                                               number2,
                                                               number3,
                                                               number4])
        #options_list_slings_short_long=[[1,0,1,0],[0,1,0,1]] # kan worden verwijdert
        # Determine actual length slings
        self.Lslings_actual = [0, 0, 0, 0]
        for i in range(4):
            self.Lslings_actual[i] = distance_points_3d(Data_SKL["Lift_points"][i],
                                                         Data_SKL["Hook_point"])
        # Determine stifness ratio slings
        self.k = [0, 0, 0, 0]

        for i in range(4):
            Asling=pi*(Data_SKL["Dslings"][i]/2)**2
            self.k[i] = stifness_ratio(Asling, 
                                       Data_SKL["Eslings"][i], 
                                       Data_SKL["Lslings"][i])

        # Determine sling force when the length slings are equal
        _Hook_point = [self.Hook_point_x, self.Hook_point_y, self.Hook_point_z]
        self.Checks_SKL["Results_normal_length"] = self.loop_skew_load(Data_SKL["Lslings"])
        F_slings_start=self.Checks_SKL["Results_normal_length"]["F_slings_total"]                                          

        self.Checks_SKL["Results_normal_length"]["sling"] =" All normal length"
        self.Checks_SKL["Results_normal_length"]["Short_long_slings"] = [1,1,1,1]
        self.Checks_SKL["Results_normal_length"]["SKL_factor"] = "N.V.T"
        Results_skl.append(self.Checks_SKL["Results_normal_length"])

        # Loop through all 16 options
        for option_sling_short_long in options_list_slings_short_long:
            # Print check kan wordne vewrijdert 

            
            # Determine length of slings based on DNV norm
            length_slings = determine_length_slings(option_sling_short_long,
                                                    Data_SKL["Lslings"])[0]
         
            # Skew load calculations
            Results_calc = self.loop_skew_load(length_slings)

            # Storing values in list
            list_loop["Length_slings"].append(length_slings) 
            list_loop["Short_long_slings"].append(option_sling_short_long)
            for key, values in Results_calc.items():
                if key not in list_loop.keys():
                    list_loop[key]=[]
                    list_loop[key].append(values)
                else:
                    list_loop[key].append(values)
            
            for i in range(4):
                F_slings_list_total[i].append(Results_calc["F_slings_total"][i])
            
            # Printen van de checks kan worden verwijdert
            print("________________CHECKS:"+str(option_sling_short_long)+"__________________")
            self.print_checks(Results_calc["Start_hook"],
                            self.F_load_total,
                            Results_calc['F_total_hook'],
                            Results_calc["Hook_point"],
                            Results_calc["F_slings_total"],
                            Data_SKL["Dslings"],
                            Data_SKL["Eslings"],
                            Results_calc["Load_dis"],
                            Results_calc["Pitch"],
                            Results_calc["Roll"])

        # Determine max skew load factor and max/min roll pitch angles
        # Determine also on which index the max sling force is 
        #Results_skl = []
        for i in range(4):
            # Determine max force of each sling
            max_F_sling = max(F_slings_list_total[i])
            index = F_slings_list_total[i].index(max_F_sling)
            row = {}
            row ["sling"] = "Sling"+str(i+1)
            for key, values in list_loop.items():
                row[key] = values[index]
            
            

            SKl_factor=max_F_sling/F_slings_start[i]
            self.Checks_SKL["SKL_factor"].append(SKl_factor)
            self.max_skew_load_factor[i] = SKl_factor
            row["SKL_factor"] = SKl_factor
            Results_skl.append(row) 
        
        df_2_skl = pd.DataFrame.from_dict(Results_skl) 
        df_2_skl.to_csv (Results_SKL_File_Path, index = False, header=True)
        
        self.values_pitch_roll_angles["Max roll"] = max(list_loop["Roll"])
        self.values_pitch_roll_angles["Min roll"] = min(list_loop["Roll"])
        self.values_pitch_roll_angles["Max pitch"] = max(list_loop["Pitch"])
        self.values_pitch_roll_angles["Min pitch"] = min(list_loop["Pitch"])
        # Print max values
        print(self.max_skew_load_factor)

        
   
   
    def print_checks(self,start_hook,F_load_total,
                     F_total_hook,Hook_point,F_slings,
                     Aslings,Eslings,Load_dis,Roll,Pitch):
        delta_hook_total=[0,0,0]
        delta_hook_total[0]=Hook_point[0]-start_hook[0]
        delta_hook_total[1]=Hook_point[1]-start_hook[1]
        delta_hook_total[2]=Hook_point[2]-start_hook[2]

        d = {"Sling1": [round(F_slings[0],2), round(Aslings[0],2),Eslings[0], round((Load_dis[0])*100,2)],
            "Sling2": [round(F_slings[1],2), round(Aslings[1],2),Eslings[1], round((Load_dis[1])*100,2)],
            "Sling3": [round(F_slings[2],2), round(Aslings[2],2),Eslings[2], round((Load_dis[2])*100,2)],
            "Sling4": [round(F_slings[3],2), round(Aslings[3],2),Eslings[3], round((Load_dis[3])*100,2)]}
        
        print("_______________________________________CHECKS___________________________________________")


        print("Pitch angle: "+str(round(Pitch,2))+"deg")
        print("Roll angle: "+str(round(Roll,2))+"deg")
        print(" ")
        print("F-load-total: "+str(round(F_load_total,2))+"N")
        print(" ")
        print ("{:22} {:<15} {:<15} {:<15}".format(" ","x[mm]", "y[mm]","z[mm]"))
        print ("{:<22} {:<15} {:<15} {:<15}".format("Start haak" ,str(round(start_hook[0],3)),str(round(start_hook[1],3)), str(round(start_hook[2],3))))
        print ("{:<22} {:<15} {:<15} {:<15}".format("Cooardinaten haak" ,str(round(Hook_point[0],3)),str(round(Hook_point[1],3)), str(round(Hook_point[2],3))))
        print ("{:<22} {:<15} {:<15} {:<15}".format("Verplaatsingen haak" ,str(round(delta_hook_total[0],3)),str(round(delta_hook_total[1],3)), str(round(delta_hook_total[2],3))))
        print (" ")
        print("Totale kracht haak(x-richting):" +str(round(F_total_hook[0],3))+"N")
        print("Totale kracht haak(y-richting):" +str(round(F_total_hook[1],3))+"N")
        print("Totale kracht haak(z-richting):" +str(round(F_total_hook[2],3))+"N")

        print("______________________________________TABLE SLINGS________________________________________________")
        print(" ")
        print ("{:<8} {:<15} {:<20} {:<20} {:<20}".format('Sling','F sling[N]','A sling[mm^2]',"E slings[N/mm^2]",'load dis[%]'))
        for k, v in d.items():
            F, A, E,load_dis = v
            print ("{:<8} {:<15} {:<20} {:<20} {:<20}".format(k,F, A, E, load_dis))
        
    def loop_skew_load(self,Length_slings):
        """_summary_
        This function calculates the forces in the sling, based
        on the sling length and the total load of the object. The loop is bases
        on diagram .. see picture:

        Args:
            Length_slings (array[1x4]): Length of slings[mm]

        Returns:
            Hook_point: End hook point x,y,z coardinates[mm]
            load_dis: Vertical load distribution of each point[%]
            F_slings_total: Forces in each sling[N]
            F_total_hook: Forces in hook x,y,z direction[N]
            Start_hook: Start postiion hook x,y,z coardinates[mm]
        """
        # Making list
        F_slings_total = [0, 0, 0, 0]
        Rek_slings_total=[0,0,0,0]
        F_total_hook = [0, 0, 0]
        
        # Step 1 Determine start hook_point
        Hook_point_loop = [0,0,0]
        Hook_point_loop = Determine_start_hook_point(self.Lift_points,
                                                  [self.Hook_point_x,
                                                  self.Hook_point_y,
                                                  self.Hook_point_z],
                                                  Length_slings)
    
        x_start_pos_hook = Hook_point_loop[0]
        y_start_pos_hook = Hook_point_loop[1]
        z_start_pos_hook = Hook_point_loop[2]
        # Start loop
        for step in range(self.steps):
            # Step 2: Determine number of slack slings 
            _slack_cables = slack_slings(self.Lift_points,
                                       Hook_point_loop,
                                       Length_slings)
            N_slack=_slack_cables.count(0)                                      

            # stap 3: Determine force in point hook 
            F_z = self.F_load_total*((step+1)/self.steps)                           
            F = [0, 0, F_z-F_total_hook[2]]    # Assumption that the x and y forces are equal to zero                                         
           
            # Determine which points have a tigth sling
            j = 0
            Lift_points_used = []
            k_used = []
            for i in range(4):
                if _slack_cables[i]==1:
                    Lift_points_used.append(self.Lift_points[i])
                    k_used.append(self.k[i])
            
            # step 4 Determine forces in slings and displacement hook
            if N_slack<2:
                results_3d_matrix=force_displacement_3d(Lift_points_used,Hook_point_loop,k_used,F)
                delta_hook=results_3d_matrix[0]
                __F_slings=results_3d_matrix[1]
                __Rek_slings=results_3d_matrix[2]
                
            else:
                results_2d_matrix=force_displacement_2d(Lift_points_used,Hook_point_loop,k_used,F)
                delta_hook=results_2d_matrix[0]
                __F_slings=results_2d_matrix[1]
                __Rek_slings=results_2d_matrix[2]
           
            #Step5: Determine total forces in sling
            j=0
            for i in range(4):
                if _slack_cables[i]==1:
                    F_slings_total[i]+=__F_slings[j]
                    Rek_slings_total[i]+=__Rek_slings[j]
                    j=j+1
                else:
                    F_slings_total[i]+=0
            
            # step 6: Determine position hook with at this iteration
            for i in range(3):
                Hook_point_loop[i]=Hook_point_loop[i]+delta_hook[i]
            
            # Step7: Determine forces in hook
            F_total_hook=[0,0,0]
            for i in range(4):
                angles=angle_3d(Hook_point_loop,self.Lift_points[i])
                F_total_hook[0] += F_slings_total[i]*angles[0]
                F_total_hook[1] += F_slings_total[i]*angles[1]
                F_total_hook[2] += F_slings_total[i]*angles[2]
            
        
        # End loop 
        # Determine load distribution
        load_dis=[0,0,0,0]
        for i in range(4):
            angles=angle_3d(Hook_point_loop,self.Lift_points[i])
            load_dis[i]=(F_slings_total[i]*angles[2])/self.F_load_total

        # Determine pitch and roll angles
        pitch_roll_angles = determine_angles_object(
                                [self.COG_x, self.COG_y, self.COG_z],
                                Hook_point_loop)

        return {"Hook_point":Hook_point_loop,
                "Load_dis":load_dis,
                "F_slings_total":F_slings_total,
                "F_total_hook":F_total_hook,
                "Start_hook":[x_start_pos_hook,
                              y_start_pos_hook,
                              z_start_pos_hook],
                "Roll":pitch_roll_angles[1],
                "Pitch":pitch_roll_angles[0],
                "Strain_slings":Rek_slings_total}
        


        
    @property 
    def get_max_skew_load_factor(self):
        return self.max_skew_load_factor

    @property 
    def get_max_min_pitch_roll_angles(self):
        return self.values_pitch_roll_angles         

    @property 
    def get_Checks_SKL(self):
        return self.Checks_SKL
    
      
    @property 
    def results(self):
        #return [self.Hook_point_list,self.F_slings_list,self.delta_length_slings_list,self.load_perc_list]
        return {"Hook_points":self.Hook_point_list,"Fslings":self.F_slings_list,"Delta_slings":self.delta_length_slings_list,"Load perc":self.load_perc_list,"Text":self.texts_step_total}
 
class Calc_load_dis:
    def __init__(self,Lift_points,_Calc_COG_env,COG,n,weight):
        
        # Getting total COG envelope from Calc_cog_env Class
        COG_env = _Calc_COG_env.get_cog_env_total
        
        # Determine total weight ob lifting object
        self.total_weight= weight
        
        # Determine which method of calculating the load dis 
        if n==1:
            self._Load_dis=[1]
            self._COG_shift_factor=[[1, 1, 1, 1, 1, 1, 1, 1]]
        if n==2:
            self._Load_dis=determine_load_dis_two_point(Lift_points[0],
                                                        Lift_points[1],
                                                        COG)
            self._COG_shift_factor=COG_shift_factor_two_point(Lift_points,
                                                              COG_env)
        
        if n==3:
            self._Load_dis=determine_load_dis_three_point(Lift_points[0],
                                                          Lift_points[1],
                                                          Lift_points[2],
                                                          COG)
            self._COG_shift_factor=COG_shift_factor_three_point(Lift_points,
                                                                COG_env)
        
        if n==4:
            self._Load_dis=determine_load_dis_four_point(Lift_points[0],
                                                         Lift_points[1],
                                                         Lift_points[2],
                                                         Lift_points[3],
                                                         COG)
           
            self._COG_shift_factor=COG_shift_factor_four_point(Lift_points,
                                                               COG_env)

    @property
    def return_load_dis(self):
        # Returning load distributie [%]
        return self._Load_dis


    @property 
    def get_load_dis_tons(self):
        # Returning load [t]
        load_dis_tons = np.round(np.multiply(np.array(self._Load_dis),
                                                    self.total_weight))
        return load_dis_tons
    
    @property
    def get_max_cog_shifts(self):
        # Returning max cog shifts
        Max_cog_shift_list=[]
        i=0
        for row in self._COG_shift_factor:
            max_cog_shift = max(row)/self._Load_dis[i]
            Max_cog_shift_list.append(max_cog_shift)
            i+=1
        return Max_cog_shift_list

    @property
    def get_max_load_dis_x(self):
        # Return max load dis only x-direction
        Max_cog_shifts_only_x=[]
        i=0
        for row in self._COG_shift_factor:
            max_row = max([row[0],row[1]])
            Max_cog_shifts_only_x.append(max_row)
            i+=1
        return Max_cog_shifts_only_x
    
    @property
    def get_max_load_dis_y(self):
        # Return max load dis only y-direction
        Max_cog_shifts_only_y=[]
        i=0
        for row in self._COG_shift_factor:
            max_row=max([row[2],row[3]])
            Max_cog_shifts_only_y.append(max_row)
            i+=1
        return Max_cog_shifts_only_y
    

    @property 
    def get_max_load_dis_both(self):
        # Return max load dis both directions
        get_max_cog_shifts_both_direction=[]
        i=0
        for row in self._COG_shift_factor:
            max_row = max([row[4],row[5],row[6],row[7]])
            get_max_cog_shifts_both_direction.append(max_row)
            i+=1
        return get_max_cog_shifts_both_direction

    @property
    def get_cog_shift_x(self):
        # Returning cog shift only x-direction 
        Max_cog_shifts_only_x=[]
        i=0
        for row in self._COG_shift_factor:
            max_row = max([row[0],row[1]])
            Max_cog_shifts_only_x.append(max_row/self._Load_dis[i])
            i+=1
        return Max_cog_shifts_only_x
    
    @property 
    def get_cog_shift_y(self):
        # Returning cog shift only y-direction
        Max_cog_shifts_only_y=[]
        i=0
        for row in self._COG_shift_factor:
            max_row = max([row[2],row[3]])
            Max_cog_shifts_only_y.append(max_row/self._Load_dis[i])
            i+=1
        return Max_cog_shifts_only_y


    

    @property
    def get_cog_shifts_total(self):
        cog_shift_calc_total={"A":{"both":[0,0],"x":[0,0],"y":[0,0]},
                                "B":{"both":[0,0],"x":[0,0],"y":[0,0]},
                                "C":{"both":[0,0],"x":[0,0],"y":[0,0]},
                                "D":{"both":[0,0],"x":[0,0],"y":[0,0]}}
        
        point_names=["A","B","C","D"]
        i=0
        for row in self._COG_shift_factor:
            max_only_x_dis=max([row[0],row[1]])
            max_only_y_dis=max([row[2],row[3]])
            max_only_both_dis=max([row[4],row[5],row[6],row[7]])
            cog_shift_calc_total[point_names[i]]["both"][0]=round(max_only_both_dis*100,1)
            cog_shift_calc_total[point_names[i]]["both"][1]=round(max_only_both_dis/self._Load_dis[i],2)
            cog_shift_calc_total[point_names[i]]["x"][0]=round(max_only_x_dis*100,1)
            cog_shift_calc_total[point_names[i]]["x"][1]=round(max_only_x_dis/self._Load_dis[i],2)
            cog_shift_calc_total[point_names[i]]["y"][0]=round(max_only_y_dis*100,1)
            cog_shift_calc_total[point_names[i]]["y"][1]=round(max_only_y_dis/self._Load_dis[i],2)
            i+=1
    
        return cog_shift_calc_total

    
    @property
    def get_max_cog_shifts_only_x_factor(self):
        Max_cog_shifts_only_x=[]
        i=0
        for row in self._COG_shift_factor:
            max_row=max([row[0],row[1]])
            Max_cog_shifts_only_x.append(max_row/self._Load_dis[i])
            i+=1
        return Max_cog_shifts_only_x
    
    @property
    def get_max_cog_shifts_only_y_factor(self):
        Max_cog_shifts_only_y=[]
        i=0
        for row in self._COG_shift_factor:
            max_row=max([row[2],row[3]])
            Max_cog_shifts_only_y.append(max_row/self._Load_dis[i])
            i+=1
        return Max_cog_shifts_only_y
    
class Calc_TEF_factor:
    def __init__(self,
                 Lift_points,
                 COG,
                 _Calc_COG_env,
                 n,
                 Data_general_factor,
                 _Calc_load_dis):

        angle_roll = Data_general_factor["TEF"][0]
        angle_pitch = Data_general_factor["TEF"][1]

        self.n=n
        self.Lift_points=Lift_points
        self.COG=COG
        # Getting info from other calculations classes 
        COG_envelope_y = _Calc_COG_env.get_cog_env_y
        COG_envelope_x = _Calc_COG_env.get_cog_env_x
        COG_envelope_both = _Calc_COG_env.get_cog_env_both
        Load_dis_y = _Calc_load_dis.get_max_load_dis_y
        Load_dis_x = _Calc_load_dis.get_max_load_dis_x
        load_dis_both = _Calc_load_dis.get_max_load_dis_both
        self.COG_env_size=_Calc_COG_env.get_cog_env_size
        # makin dictionary so it can store all checks 
        self.checks_end_TEF={"ANS_envelope_TILT": None,
                            "ANS_TILT_Angles":None,
                            "Tilt_angle":None}
        # Making list so it can store all inputparameters
        Check_list={"Lift_points": [],
                    "COG_point": [],
                    "Angles": [],
                    "Load_dis": []}
        # De normal vector hangt af van de hoeken, dus die moet elke keer opniuwe worden berekend, vogende stap
        self.Lift_points=Lift_points
        self.TEF_factor=[]
        
        if angle_roll == 0 and angle_pitch==0:
            for i in range(self.n):
                self.TEF_factor.append(1)
        else:
            if angle_pitch==0:
                Load_dis_without_tilt = Load_dis_y
                COG_envelope = COG_envelope_y
                self.checks_end_TEF["ANS_envelope_TILT"]=" Envelope only y-direction"
                self.checks_end_TEF["ANS_TILT_Angles"]="only roll"
                self.checks_end_TEF["Tilt_angle"]="Roll: "+str(angle_roll)+"[deg]" 
                angles_list=[[angle_roll,0],[-angle_roll,0]]
            elif angle_roll==0:
                Load_dis_without_tilt = Load_dis_x
                COG_envelope = COG_envelope_x
                angles_list=[[0,angle_pitch],[0,-angle_pitch]]
                self.checks_end_TEF["ANS_envelope_TILT"]=" Envelope only x-direction"
                self.checks_end_TEF["ANS_TILT_Angles"]="only pitch"
                self.checks_end_TEF["Tilt_angle"]="Pitch: " + str(angle_pitch)+"[deg]"
            else:
                Load_dis_without_tilt = load_dis_both
                COG_envelope = COG_envelope_both
                angles_list=[[angle_roll,angle_pitch],
                            [-angle_roll,-angle_pitch],
                            [-angle_roll,angle_pitch],
                            [angle_roll,-angle_pitch]]  
                self.checks_end_TEF["ANS_envelope_TILT"]=" Both directions"
                self.checks_end_TEF["ANS_TILT_Angles"]="both roll and pitch "
                self.checks_end_TEF["Tilt_angle"]="Pitch:" + str(angle_pitch)+"[deg] " + "Roll: "+str(angle_roll) +"[deg"

            #print(angles_list)
            #print(COG_envelope)
            #print(Load_dis_without_tilt)       

            load_dis_tilt_list=[]
            for i in range(self.n):
                load_dis_tilt_list.append([])

            for angles in angles_list:
                
                angles_nv = self.determine_angles_normal_vector(angles)
                lift_points_tilt= self.determine_lift_points(angles,
                                                             angles_nv)
                COG_envelope_tilt= self.COG_envelope_tilt(angles,
                                                        COG_envelope,
                                                        angles_nv)


                for COG_point_tilt in COG_envelope_tilt:
                    load_dis_with_tilt=self.load_dis(COG_point_tilt,
                                                    lift_points_tilt)
                    for i in range(self.n):
                        load_dis=load_dis_with_tilt[i]
                        load_dis_tilt_list[i].append(load_dis)
                    Check_list["Lift_points"].append(lift_points_tilt)
                    Check_list["COG_point"].append(COG_point_tilt)
                    Check_list["Angles"].append([angles[1],angles[0]])
                    Check_list["Load_dis"].append(load_dis_with_tilt)
                    
            checks_TEF={}
            for i in range(self.n):
                # Determine max TEF factor
                max_load_dis=max(load_dis_tilt_list[i])
                index= load_dis_tilt_list[i].index(max_load_dis)
                TEF_factor=max_load_dis/Load_dis_without_tilt[i]
                if TEF_factor<1:
                    self.TEF_factor.append(1)
                else:
                    self.TEF_factor.append(TEF_factor)
                # Storing results
                for key, values in Check_list.items():
                    if key not in checks_TEF.keys():
                        checks_TEF[key] = []
                        checks_TEF[key].append(values[index])
                    else:
                        checks_TEF[key].append(values[index])

            
            self.clean_up_data(checks_TEF)

        # making list so that the max value can be determined 
        self.angle_roll=angle_roll
        self.angle_pitch=angle_pitch

    def determine_angles_normal_vector(self,angles):
        """_summary_
        This function calculates the 

        Step 1:
        Determine the 3 points

        Step 2:
        Determine the two vectors

        Step 3:
        Determine the cross product of those two vectors
        

        args:
            angles[array[1x2]: angles[0]= Roll angle[deg]
                               angles[1]= Pitch angle[deg]
        Note:
            v_point_upper= to the vector from COG to cube point upper
            v_point_lower to the vector from COG to cube point lower
            It is only calculates ones, because all upper and lower 
            cube points have the same length

        """
        # Step 1 determine normal vector of the plane
        # Determine 3 points on plane[x,y,z]
        # point 1 is equal to the COG, only the z-coardinaat is equal to 0
        point1=[0,0,0]
        # Point 2 is determined by the pitch, and lie on the y-axes
        point2=[0,0,0]
        point2[0]=math.cos(math.radians(angles[1]))
        point2[2]=math.sin(math.radians(angles[1]))
        # Point 3 is determined by the roll, and lies on the x-axes
        point3=[0,0,0]
        point3[1]=math.cos(math.radians(angles[0]))
        point3[2]=math.sin(math.radians(angles[0]))

        vector1=np.array(point2)
        vector2=np.array(point3)

        # Determine the cross product of the two vectors
        # This vector is equal to the normal vector of the plane 
        vector3=np.cross(vector1,vector2)
        return angle_3d(point1,vector3)

    def load_dis(self,COG,Lift_points):
        if self.n==1:
            _load_dis_with_tilt_angle=[1]
        if self.n==2:
            _load_dis_with_tilt_angle=determine_load_dis_two_point(Lift_points[0],Lift_points[1],Lift_points)
        if self.n==3:
            _load_dis_with_tilt_angle=determine_load_dis_three_point(Lift_points[0],Lift_points[1],Lift_points[2],COG)
        if self.n==4:
            _load_dis_with_tilt_angle=determine_load_dis_four_point(Lift_points[0],Lift_points[1],Lift_points[2],Lift_points[3],COG)
       
        
        return _load_dis_with_tilt_angle

    def COG_envelope_tilt(self,angles,COG_envelope,angles_Nv):
        """_summary_
        This function calculates all point possibilities of the envelope cube.
        

        Step 1:
        Calculate the x and y position on plane 1,
        this will be done by using delta x and delta y
        This is not precise there is an error of max 1 mm
    
        Step 1:
        Determine the two vector lengts of the cog cube:
        Length1= Length vector to outer lower COG cube point
        Length2= Length vector to outer upper COG cube point
        Step 3:
        Determine angles of perpendicular vector to the plane 
        Step 4: 
        Determine point x,y coardinates 
        

        args:
            angles[array[1x2]: angles[0]= Roll angle[deg]
                               angles[1]= Pitch angle[deg]
        Note:
            v_point_upper= to the vector from COG to cube point upper
            v_point_lower to the vector from COG to cube point lower
            It is only calculates ones, because all upper and lower 
            cube points have the same length

        """
        # Step 1: Determine the vector length

        Length1=self.COG[2]+self.COG_env_size[2]*0.5
        Length2=self.COG[2]-self.COG_env_size[2]*0.5
        
        # Step 2:
        COG_envelope_with_tilt=[]
        for point in COG_envelope:
            x_dif= point[0]-self.COG[0]
            y_dif= point[1]-self.COG[1]
            x_plane_1= math.cos(math.radians(angles[1]))* x_dif + self.COG[0]
            y_plane_1= math.cos(math.radians(angles[0]))* y_dif + self.COG[1]
            
            COG_x_lower = x_plane_1 + angles_Nv[0]* Length1
            COG_x_upper = x_plane_1 + angles_Nv[0]* Length2
            COG_y_lower = y_plane_1 + angles_Nv[1]* Length1
            COG_y_upper = y_plane_1 + angles_Nv[1]* Length2
            COG_envelope_with_tilt.append([COG_x_lower,COG_y_lower])
            COG_envelope_with_tilt.append([COG_x_upper,COG_y_upper])
        return COG_envelope_with_tilt
        
    def determine_lift_points(self,angles,angles_Nv):
        """_summary_
        This function calculates the lift point with the given angles 
        The first step is determine the coardinates of the lifitng point 
        on plane 1 

        The second step is to calculated the lifting points, based on
        the z-coardinates of the lifting points

        args:
            angles[array[1x2]: angles[0]= Roll angle[deg]
                               angles[1]= Pitch angle[deg]

        """
        lift_points_tilt=[]
        for i in range(self.n):
            lift_point_tilt = [0,0,0]
            x_dif= self.Lift_points[i][0]-self.COG[0]
            y_dif= self.Lift_points[i][1]-self.COG[1]
            # Step 1
            x_plane_1= math.cos(math.radians(angles[1]))* x_dif + self.COG[0]
            y_plane_1= math.cos(math.radians(angles[0]))* y_dif + self.COG[1]

            lift_point_tilt[0]=x_plane_1 + self.Lift_points[i][2]* angles_Nv[0]
            lift_point_tilt[1]=y_plane_1 + self.Lift_points[i][2]* angles_Nv[1]
            lift_points_tilt.append(lift_point_tilt)
        return lift_points_tilt

    def clean_up_data(self,checks_TEF):
        """_summary_
        In this function the data of the checks will be cleaned up 
        ,because all input parameters of the MAX tef factors are stored. 
        But whith some MAX tef factors the in put parameters are the same
        Returns:
            _type_: _description_
        """
        point_names =["A","B","C","D"]
        angles_list=[]
        indexen=[]
        points= []
        j=0
        i=0

        for angles in checks_TEF["Angles"]:
            if angles not in angles_list:
                angles_list.append(angles)
                indexen.append(checks_TEF["Angles"].index(angles))
                points.append([point_names[i]])
            else:
                points[j].append(point_names[i])
                j +=1
            i +=1

        
        self.checks_end_TEF["Points"]=points
        for key, values in checks_TEF.items():
            self.checks_end_TEF[key]=[ ]
            for index in indexen:
                self.checks_end_TEF[key].append(values[index])

                
    @property
    def get_TEF_checks(self):
        return self.checks_end_TEF

 
    @ property 
    def get_angles(self):
        if self.angle_pitch == 0 and self.angle_roll == 0:
            text = "No tilt angles, factor = 1"
        elif self.angle_pitch != 0 and self.angle_roll ==0: 
            text ="Only pitch angle: " + str(self.angle_pitch) +"deg"
        elif self.angle_roll != 0 and self.angle_pitch ==0:
            text ="Only roll angle: " + str(self.angle_roll) + "deg"
        else: 
            text= "Pitch: " +str(self.angle_pitch) +"deg/ Roll: "+str(self.angle_roll)+"deg"
        return text
    
    @property 
    def get_tef_factors(self):
        return self.TEF_factor

class Calc_factors:
    def __init__(self,data_general_factor,
                      _Calc_load_dis,
                      weight,
                      data_SSF_factor,
                      N_lifts,
                      _Calc_TEF_factor):
        """_summary_
        This class desrebis all general factors, and also the slings safety factors

        Args:
            _Answers_general_factor (dictionary): Answers dropdownmenu
        Note:
            Factors Daf AND tef needs calculations that is why they cannot be determined by function factors_no_calculations

        """
        # Getting COG shift from Calc_load dis class and TEF factor from calc class
        TEF_factors = _Calc_TEF_factor.get_tef_factors
        COG_shifts = _Calc_load_dis.get_max_cog_shifts
        self.general_factors={}
        # WCF/COGcrane/YAW factors determined
        for key,values in data_general_factor.items():
            if key !="DAF" and key!="TEF" and key!="COG_envelope" and key != "SKL_analysis":
                self.general_factors[key]=factors_no_calculations(key,values)

        # COG shift factor
        if data_general_factor["COG_envelope"] == "Use of COG envelope":
            self.general_factors["COG_envelope"] = COG_shifts
        else:
            lst_cog_shift = []
            for i in range(N_lifts):
                lst_cog_shift.append(1.1)
            self.general_factors["COG_envelope"] = lst_cog_shift

        # DAF factor       
        self.general_factors["DAF"] = daf_factor(weight,
                                                 data_general_factor["DAF"])
        self.general_factors["TEF"] = TEF_factors
        # Making sling safety factor 
        self.SSF_factors_total = []
        
        i=1
        for row in data_SSF_factor:
            ssf_factors = {}
            
            ssf_factors["Consequence_factor"] = row["Consequence_factor"]
            ssf_factors["Lift_factor"] = row["Lift_factor"]

            ssf_factors["Material_factor"] = factors_no_calculations(
                                                "Material_factor",
                                                row["Material_factor"]
            )
            ssf_factors["Wear_application_factor"] = factors_no_calculations(
                                                "Wear_application_factor",
                                                row["Wear_application_factor"]
            )
            SSF = np.prod([ssf_factors["Consequence_factor"],
                           ssf_factors["Lift_factor"],
                           ssf_factors["Material_factor"],
                           ssf_factors["Wear_application_factor"]])
            if SSF < 2.3 :
                SSF = 2.3 
            txt = "SSF"+str(i)
            self.general_factors[txt] = SSF
            ssf_factors["sling"] = txt
            ssf_factors["SSF"] = SSF
            self.SSF_factors_total.append(ssf_factors)
            i +=1


    @property
    def get_general_factors(self):
        return self.general_factors
    
    @ property 
    def get_SSF_factors_total(self):
        return self.SSF_factors_total
  
class Calc_rigging:    
    def __init__(self,
                Data_rigging,
                _Calc_factors,
                _Calc_load_dis,
                weight,
                SKL_results,
                Data_rigging_other):
        
        # Getting values from other calc classes 

        self._Calc_load_dis=_Calc_load_dis
        general_factors = _Calc_factors.get_general_factors
        self.TEF_factors = general_factors["TEF"]
        


        # Factors 
        DAF=general_factors["DAF"]
        WCF=general_factors["WCF"]
        YAW=general_factors["YAW"]


        # Making checks other equipment
        self.Rigging_other_calc_total={}
        
        #self.checks_other_equipment(_Answers_other_rigging,
                                    #FDRL,
                                    #)
        # Stap 1 bepalen FDRL 
        FDRL=weight*WCF*DAF*YAW
        
        self.checks_other_equipment(Data_rigging_other,
                                    FDRL,
                                    SKL_results)
        self.Rigging_calc_total={}
        
        for checks in Data_rigging:
            Calc = checks
            
            # step 2 Determine factored dynamic rigging load
            # FDRL = LW*WCF*DAF*TEF*YAW
            Calc["TEF"] = self.TEF_factor(Calc["Points"])
            Calc["FDRL"] = FDRL*Calc["TEF"]

            # Step 3 determine load perc on rigging
            Calc["perc"] = self.Load_lifting_point(Calc["Points"])
            
            # stap 3 determine COG shift factor
            Calc["COG"] = self.COG_shift_factor(Calc["Points"])
        

            # Stap 4 bepalen skew load factor 
            if Calc["SKL"][0] != Fact_text["SKL"][3]:
                Calc["SKL"][2] = factors_no_calculations("SKL",Calc["SKL"][0])
            else:
                Calc["SKL"][2] = SKL_results[int(Calc["SKL"][1])-1]
            # step 5 Determine vertical load to lifting point
            # VLLP= FDRL * perc* COG*SKL
            
            Calc["VLLP"] = np.prod([Calc["FDRL"],
                                    Calc["perc"],
                                    Calc["COG"],
                                    Calc["SKL"][2]])
            
            # step 6 Determine vertical load on sligns
            #VLUS = VLLP + (RWP*DAF*WCF)
        
            Rigging_factored_load = np.prod([Calc["RWP"],
                                             DAF,
                                             WCF])

            Calc["VLUS"] = Calc["VLLP"]+Rigging_factored_load

            # step 7: Determine inline force slings
            # Angle=(tan(angle_1)^2+tan(angle_2)^2)^0.5
            # IFUS= angle * VLUS
            Angle_1 = math.tan(math.radians(Calc["Angle_1"]))
            Angle_2 = math.tan(math.radians(Calc["Angle_2"]))
            Angle_inline = math.sqrt((Angle_1**2+Angle_2**2+1))
            Calc["IFUS"] = Angle_inline*Calc["VLUS"]
            
            #step 8 Determine SLDF dis/ factor
            Calc["SLDF_dis"] = factors_no_calculations("SLDF",
                                                        Calc["SLDF_ans"])

            Calc["SLDF"] = self.SLFD_factor(Calc["SLDF_dis"],
                                                 Calc["sling"][-1],
                                                 Calc["sling"][1])

            #step 9 Determine inline force one part 
            # IFUP= (IFUS/n_parts)*n_parts
            Calc["IFUP"] = (Calc["IFUS"]/Calc["sling"][-1])*Calc["SLDF"]

            # step 10 Determine bending ruducing factor
            Calc["min_d"] = min(Calc["Connection_upper"][1],
                                Calc["Connection_lower"][1])
            Calc["BRF"]=self.BRF_factor(Calc["Material"],
                                             Calc["sling"][3],
                                             Calc["min_d"],
                                             Calc["sling"][1])

            # step 11 Determine termination factor
            Calc["TRF"] = factors_no_calculations("TRF", 
                                                  Calc['TRF_ans'])

            # step 12 Determine reduction factor
            # Is the max of BRF and TRF, see paragraph 16.4.6.1
            Calc["Red_factor"] = max(Calc["BRF"], Calc["TRF"])
            
            # step 13 Determine SSF factor 
            Calc["SSF"] = general_factors[Calc["SSF_ans"]]
            # Step 14 Determine req swl sling grommet 
            # SWL req= IFUP*SSF*Reduction factor 

            swl_sling_req = np.prod([Calc["IFUP"],
                                             Calc["SSF"],
                                             Calc["Red_factor"]]
                                                   )
            uc_sling = swl_sling_req/Calc["sling"][2]
            # step 15 Determine unity check sling
            Calc["sling"].append(swl_sling_req)
            Calc["sling"].append(uc_sling)
            
            #Step 16 unity checks shackles
            # SWL req= IFUF/DAF (see lifting shee )

            if "shackle" in Calc["Connection_upper"][0].lower():
                swl_req = Calc["IFUP"]/DAF
                uc = swl_req / Calc["Connection_upper"][2]
                Calc["Connection_upper"].append(swl_req)
                Calc["Connection_upper"].append(uc)  
                
            else:
                Calc["Connection_upper"].append("N.V.T")
                Calc["Connection_upper"].append("N.V.T") 

            if "shackle" in Calc["Connection_lower"][0].lower():
                swl_req = Calc["IFUP"]/DAF
                uc = swl_req / Calc["Connection_lower"][2]
                Calc["Connection_lower"].append(swl_req)
                Calc["Connection_lower"].append(uc)  
                
            else:
                Calc["Connection_lower"].append("N.V.T")
                Calc["Connection_lower"].append("N.V.T") 

            self.Rigging_calc_total.update({Calc["Name"]:Calc})

    def checks_other_equipment(self,
                               Data_other_rigging,
                               FDRL,
                               SKL_results):

        for values in Data_other_rigging:
            row=values
            # Determine info equipment
            print(values)
            row["Ans_skl"]=values["SKL"]
            row["COG"] = self.COG_shift_factor(row["Points"])
            row["Perc"]=self.Load_lifting_point(row["Points"])
            row["TEF"]=self.TEF_factor(row["Points"])
            if row["SKL"][0] != Fact_text["SKL"][3]:
                row["SKL"][2] = factors_no_calculations("SKL",row["SKL"][0])
            else:
                row["SKL"][2] = SKL_results[int(row["SKL"][1])-1]
            # The maxixum dynamic rigging load 
            row["FDRL"]=FDRL
            row["MDRL"]=np.prod([FDRL,
                                 row["COG"],
                                 row["TEF"],
                                 row["Perc"],
                                 row["SKL"][2]])
            print(row["MDRL"])
            row["Uc"]=row["MDRL"]/float(row["WLL"])
            self.Rigging_other_calc_total.update({row['name']:row})


    def TEF_factor(self,points):
        """_summary_
        This function determines, which
        tef factor suits with the point


        """
        # getting tef factors 
        
        point_index=None
        for point in points:
            if point=="A":
                point_index=0
            if point=="B":
                point_index=1
            if point=="C":
                point_index=2
            if point=="D":
                point_index=3
        
        return self.TEF_factors[point_index]


    def Load_lifting_point(self,points):
        """_summary_
        This function determines, which
        load perc factor suits with the point

        """
        # Gettting laod perc from calc load dis class
        load_perc = self._Calc_load_dis.return_load_dis         
        point_index=[]
        for point in points:
            if point=="A":
                point_index.append(0)
            if point=="B":
                point_index.append(1)
            if point=="C":
                point_index.append(2)
            if point=="D":
                point_index.append(3)


        if len(point_index)==1:
            load_perc=load_perc[point_index[0]]
        if len(point_index)==2:
            load_perc=load_perc[point_index[0]]+load_perc[point_index[1]] 
        if len(point_index)==3:
            load_perc=load_perc[point_index[0]]+load_perc[point_index[1]] +load_perc[point_index[2]]
        if len(point_index)==4:
            load_perc=load_perc[point_index[0]]+load_perc[point_index[1]]  +load_perc[point_index[2]]+load_perc[point_index[3]]

        return load_perc

    def COG_shift_factor(self,points):
        """_summary_
        This function determines, which
        COG shift  factor suits with the point

        """ 
        # Getting COG shifts from load dis class 
        COG_shift_x = self._Calc_load_dis.get_cog_shift_x
        COG_shift_y = self._Calc_load_dis.get_cog_shift_y
        COG_shift_both = self._Calc_load_dis.get_max_cog_shifts             
        point_index=[]
        for point in points:
            if point=="A":
                point_index.append(0)
            if point=="B":
                point_index.append(1)
            if point=="C":
                point_index.append(2)
            if point=="D":
                point_index.append(3)
        
        if len(point_index)==1:

            COG_shift=COG_shift_both[point_index[0]]
        if len(point_index)==2:
            if point_index.count(0)==1 and point_index.count(1)==1:
                COG_shift=COG_shift_y[0]
            elif point_index.count(0)==1 and point_index.count(3)==1:
                COG_shift=COG_shift_x[0]
            elif point_index.count(1)==1 and point_index.count(2)==1:
                COG_shift=COG_shift_x[1]
            elif point_index.count(2)==1 and point_index.count(3)==1:
                COG_shift=COG_shift_y[3]
        if len(point_index)==3:
            COG_shift=1
        if len(point_index)==4:
            COG_shift=1



        return COG_shift

    def SLFD_factor(self,SLDF,n_parts,type):
        """_summary_
        This function calculates the SLDF factor, 
        based on the number of parts, the sling load distribution 
        and the type of sling
        Args:
            SLDF (array[1x2]): Gives the load dis of the slings see DNV
            n_parts (int):  Number of parts of the sling
            type (str): Which type is the sling

        Returns:
            SLDF_factor: SLDF factor
        Note:
            When there is a grommet used the amount of parst is
            multiplied by two
        """
        
      
        perc_1 = float(SLDF.split(":",1)[0])
        perc_2 = float(SLDF.split(":",1)[1])

        max_perc_sling_load_dis=max([perc_1,perc_2])/100
        
        type=type.lower()
        str_1="grommet"

        # Determine if the type is a grommet or a sling
        if str_1 in type:
            
            n_parts=n_parts*2

        # Calculates the sldf factor(see excel lifting sheet for formula)
        SLFD_factor=max_perc_sling_load_dis**(math.log(n_parts,2))/(1/n_parts)
        return SLFD_factor

    def BRF_factor(self,material,d,D,type):
        """_summary_
        This function calculates the bending reduction factor 
        see DNV chapter 16.4.8

        Args:
            material (str): Material type slings/grommet
            d (float): The minimum diameter over which the 
                        sling body, sling eye, 
                        or grommet is bent[mm]
            D (foat): The sling or cable laid rope diameter[mm]
            type (str): type of lifting tool

        Returns:
            BRF: Bending reduction factor
        """
        if material=="Fibre":
            BRF=1
        else:
            BRF=1/(1-(0.5/math.sqrt(D/d)))
        
            if type=="sling":
                BRF=BRF*0.935
        
        return BRF


    @property
    def get_rigging_calc_total(self):
        return self.Rigging_calc_total

    @property
    def get_rigging_other_equipment(self):
        return self.Rigging_other_calc_total

class Calc_crane:
    def __init__(self,
                Data_crane,
                _Calc_factors,
                _Calc_load_dis,
                weight):

        """_summary_:
        This  class determine the crane verification.
       

        Args:
            _answers_crane (dict):   keys(str): Cranes(depends of number of cranes)
                                    Values(array[1x3]): Values[0]= Dict_hoist(see below)
                                                        Values[1]= Name crane
                                                        Values[2]=  DDF
                                    Dict_hoist[dict]:   keys= Hoists(depend on number of hoist)
                                                        Values[-1]= Rigging weight
                                                        Values[-2]= Offlead[deg]
                                                        Values[-3]= Capacity[t]
                                                        Valeus[0:]: Points connected
            general_factors(dict): General factors 
            Calc_load_dis(class): The load distribution calculations
            Calc_tilt_factor(class): The tilt factor calculations
            weight(dict): Weight of lifting objects/rigging equipment[t]

        Returns:
            load_dis[[1x4]array]:   load_dis[0]= Point A dis[-]
                                    load_dis[1]= Point B dis[-]
                                    load_dis[2]= Point C dis[-]
                                    load_dis[3]= Point C dis[-]
        """
        # Getting values from other calc classes 

        self._Calc_load_dis=_Calc_load_dis
        general_factors = _Calc_factors.get_general_factors
        self.TEF_factors = general_factors["TEF"]       
        
        #print(_answers_crane) # Kan worden verwijdert
        # Calculate FDCL
        FDCL=np.prod([weight,
                      general_factors["WCF"],
                      general_factors["DAF"],
                      general_factors["COGCrane"]])

        self.Crane_checks = {}
        for crane, Crane_data in Data_crane.items():
            Hoist_checks = {}
            Crane_ddf = Crane_data["DDF"]
            self.Crane_checks.update({crane:{"DDF":Crane_ddf}})
            for hoist, data_hoist in Crane_data.items():

                if hoist != "DDF":
                    info={}

                    info["CAP"] = data_hoist["Data"][0]
                    info["Offlead"] = data_hoist["Data"][1]
                    info["RW"] = data_hoist["Data"][2]
                    info["Points"] = data_hoist["Points"]
                    info["perc"] = self.Load_lifting_point(info["Points"])
                    info["TEF"] = self.TEF_factor(info["Points"])
                    info["FDCL"] = FDCL * info["TEF"]
                    # Calculating HLV 
                    # HLV = FDCL * perc + RW * DAF / DDF
                    info["HLV"]=(FDCL*info["perc"]*1+info["RW"]*general_factors["DAF"])/Crane_ddf
                    # Calculating HL
                    # HL = hlv/ cos(offlead)
                    offlead_value = math.cos(math.radians(info["Offlead"]))
                    info["HL"] = info["HLV"]/offlead_value
                    info["UC"] = info["HL"]/info["CAP"]
                    self.Crane_checks[crane].update({hoist:info})






    def TEF_factor(self,points):
        """_summary_
        This function determines, which
        tef factor suits with the point


        """
        # getting tef factors 
        
        point_index=None
        for point in points:
            if point=="A":
                point_index=0
            if point=="B":
                point_index=1
            if point=="C":
                point_index=2
            if point=="D":
                point_index=3
        
        return self.TEF_factors[point_index]


    def Load_lifting_point(self,points):
        """_summary_
        This function determines, which
        load perc factor suits with the point

        """
        # Gettting laod perc from calc load dis class
        load_perc = self._Calc_load_dis.return_load_dis         
        point_index=[]
        for point in points:
            if point=="A":
                point_index.append(0)
            if point=="B":
                point_index.append(1)
            if point=="C":
                point_index.append(2)
            if point=="D":
                point_index.append(3)


        if len(point_index)==1:
            load_perc=load_perc[point_index[0]]
        if len(point_index)==2:
            load_perc=load_perc[point_index[0]]+load_perc[point_index[1]] 
        if len(point_index)==3:
            load_perc=load_perc[point_index[0]]+load_perc[point_index[1]] +load_perc[point_index[2]]
        if len(point_index)==4:
            load_perc=load_perc[point_index[0]]+load_perc[point_index[1]]  +load_perc[point_index[2]]+load_perc[point_index[3]]

        return load_perc
    
    @property 
    def get_crane_results(self):
        return self.Crane_checks


               





