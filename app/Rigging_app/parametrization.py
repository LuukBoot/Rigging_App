
from viktor.parametrization import Parametrization, Tab, OptionField, \
    DynamicArray, TextField, Text, NumberField, LineBreak, Table, \
    Section, AutocompleteField,BooleanField, Lookup, RowLookup, \
    MultiSelectField


from .Default_inputs import Table_Lift_points, Fact_text, Fact_values,\
    get_SSF_options, get_point_options, Table_slings_grommets,df_rigging, \
        Table_connect
drop_list_connect = df_rigging["drop_list_connect"]
class Parametrization(Parametrization):
    
    # Tab1: general
    tab_1 = Tab("General")
    # Tab1.section1: Lifting points 
    tab_1.section_1 = Section("Lift pointsss")
    tab_1.section_1.N_lifts = NumberField("Number of lifting points",
                                          min = 1,max = 4,
                                          default = 1,name = "N_lifts")
    tab_1.section_1.Lift_points_table = Table("Lift points",
                            default= Table_Lift_points)
    tab_1.section_1.Lift_points_table.point = TextField("Lift point")
    tab_1.section_1.Lift_points_table.x = NumberField("x",suffix = "m")
    tab_1.section_1.Lift_points_table.y = NumberField("y",suffix = "m")
    tab_1.section_1.Lift_points_table.z = NumberField("z",suffix = "m")
    tab_1.section_1.COG_x = NumberField("COG x",default = 0,suffix = "[m]")
    tab_1.section_1.COG_y = NumberField("COG y",default = 0,suffix = "[m]")
    tab_1.section_1.COG_z = NumberField("COG z",default = 0,suffix = "[m]")
    # Tab1.section2: Object geometry
    tab_1.section_2 = Section("Object geometry")
    tab_1.section_2.Object_x = NumberField("Object lengte",default = 0,
                                         suffix = "m")
    tab_1.section_2.Object_y = NumberField("Object width",default=0,
                                         suffix = "m")
    tab_1.section_2.Object_z = NumberField("Object height",default=0,
                                         suffix = "m")
    # Tab1.section_3: Weight (moet nog naar gekeken worden wat er verwijdert kan wroden)
    tab_1.section_3 = Section("Object and rigging weight")
    tab_1.section_3.LW = NumberField("LW: Weight lifted object",
                                    default = 100,suffix = "t",flex = 40)

    # Tab2: Factors 
    # Tab2.section1: General factors
    tab_2 = Tab("Factors")
    tab_2.section_1 = Section("General factors")
    tab_2.section_1.WCF = AutocompleteField("Weight of object",
                            options =  Fact_text["WCF"],
                            default =  Fact_text["WCF"][0],
                            flex = 60)
    tab_2.section_1.lb1 = LineBreak()
    tab_2.section_1.COGCrane = AutocompleteField("COG shift crane",
                            options =  Fact_text["COGCrane"],
                            default =  Fact_text["COGCrane"][0],
                            flex = 60)
    tab_2.section_1.lb2 = LineBreak()
    tab_2.section_1.DAF = AutocompleteField("Dynamic amplification factor",
                            options =  Fact_text["DAF"],
                            default =  Fact_text["DAF"][0],
                            flex = 60)
    tab_2.section_1.lb3 = LineBreak()
    tab_2.section_1.YAW = AutocompleteField("YAW effect factor",
                            options =  Fact_text["YAW"],
                            default =  Fact_text["YAW"][0],
                            flex = 60)
    tab_2.section_1.lb4 = LineBreak()
    tab_2.section_1.COG_envelope = AutocompleteField("COG envelope",
                        options =  Fact_text["COG_envelope"],
                        default =  Fact_text["COG_envelope"][0],
                            flex=60)

    tab_2.section_1.lb5 = LineBreak()


    tab_2.section_1.TEF_x_bool=BooleanField("Are the hooks above the x-axes different as below?",
                        name = "TEF_x_bool",
                        flex = 60)
    tab_2.section_1.TEF_x_angle = NumberField("Which tilt angle",
                        visible = Lookup("TEF_x_bool"),
                        default = 0,suffix = "deg",
                        description = " See paragraph 16.2.4.3, (One vessel: 3deg, Two vessels: 5deg )")
    tab_2.section_1.lb6 = LineBreak()

    tab_2.section_1.TEF_y_bool = BooleanField("Are the hooks left from the y-axes different from the right?",
                                name="TEF_y_bool",
                                flex = 60)
    tab_2.section_1.TEF_y_angle = NumberField("Which pitch angle",
                        visible=Lookup("TEF_y_bool"),
                        default = 0,suffix="deg",
                        description = " See paragraph 16.2.4.3, (One vessel: 3deg, Two vessels: 5deg )")
    # Tab2.section2: Sling safety factors
    tab_2.section_2 = Section("sling safety")
    tab_2.section_2.SSF_data = DynamicArray("Sling safety factor",
                        min= 1, row_label = "Sling")
    tab_2.section_2.SSF_data.lift_factor_bool = BooleanField("Lift factor calculated? (default=1.3)",
                                            description="See dnv 16.4.4",flex=60)
    tab_2.section_2.SSF_data.lift_factor = NumberField("What is the detailed calculation",
                                            visible=RowLookup("lift_factor_bool"),default=1)
    tab_2.section_2.SSF_data.lb1 = LineBreak()
    tab_2.section_2.SSF_data.consequence_factor_bool = BooleanField("The consequence factor (default=1.3) ",
                                            description="See dnv 16.4.5",flex=60)
    tab_2.section_2.SSF_data.consequence_factor = NumberField("Reduced consequence factor",
                                            visible=RowLookup("consequence_factor_bool"),default=1)
    tab_2.section_2.SSF_data.lb2= LineBreak()
    tab_2.section_2.SSF_data.Material_factor = AutocompleteField("Material factor",
                                    options =  Fact_text["Material_factor"],
                                    default =  Fact_text["Material_factor"][0],
                                    description="See dnv 16.4.9",
                                    flex = 60)
    tab_2.section_2.SSF_data.lb3= LineBreak()
    tab_2.section_2.SSF_data.Wear_application_factor = AutocompleteField("Wear and applicaton factor",
                                    options =  Fact_text["Wear_application_factor"],
                                    default =  Fact_text["Wear_application_factor"][0],
                                    description="See dnv 16.4.9",
                                    flex = 60)
    
    # Tab 3: Rigging 
    # Tab 3.section1 : Rigging General data
    tab_3 = Tab("Rigging")
    tab_3.section_1 = Section("Rigging general")
    tab_3.section_1.Rigging_data = DynamicArray("Rigging",min = 1)
    tab_3.section_1.Rigging_data.RiggingPoint = TextField("Rigging point",
                                            default = "Name of this point")
    tab_3.section_1.Rigging_data.rigging_material = AutocompleteField("",
                                            options = ["Steel","Fibre"],
                                            default = "Steel")
    tab_3.section_1.Rigging_data.Points = MultiSelectField(" ",
                                        options = get_point_options,
                                        )
    tab_3.section_1.Rigging_data.lb1 = LineBreak()
    tab_3.section_1.Rigging_data.RWP = NumberField("Rigging weight above lifting point",
                                        default = 0,
                                        suffix = "t",
                                        flex = 60)
    tab_3.section_1.Rigging_data.lb2 = LineBreak()
    tab_3.section_1.Rigging_data.transvere_angle = NumberField("Sling angle with vertical transverse",
                                        default = 0,
                                        suffix = "deg",
                                        flex = 60)
    tab_3.section_1.Rigging_data.lb3 = LineBreak()
    tab_3.section_1.Rigging_data.longitudinal_angle = NumberField("Sling angle with vertical longitudinal_angle",
                                        default = 0,
                                        suffix = "deg",
                                        flex = 60)
    tab_3.section_1.Rigging_data.lb4 = LineBreak()
    tab_3.section_1.Rigging_data.SSF = OptionField("Sling safety factor",
                                        options = get_SSF_options,
                                        flex = 60)
    tab_3.section_1.Rigging_data.lb5 = LineBreak()
    tab_3.section_1.Rigging_data.TRF = AutocompleteField("Terminationfactor" ,
                                        options = Fact_text["TRF"],
                                        default = Fact_text["TRF"][0],
                                        description = "See dnv 16.4.7",
                                        flex = 60)
    tab_3.section_1.Rigging_data.lb6 = LineBreak()
    tab_3.section_1.Rigging_data.SKL = AutocompleteField("Skew load factor",
                                        options = Fact_text["SKL"],
                                        default = Fact_text["SKL"][0],
                                        flex = 60)
    tab_3.section_1.Rigging_data.SKL_value = AutocompleteField("Which skew load factor is it?",
                                        options = ["1","2","3","4"],
                                        default = "1")
    tab_3.section_1.Rigging_data.lb7 = LineBreak()
    tab_3.section_1.Rigging_data.SLDF = AutocompleteField("SLFD factor",
                                        options = Fact_text["SLDF"],
                                        default = Fact_text["SLDF"][0],
                                        flex = 100)
    # Table for slings/ grommets 
    tab_3.section_1.Rigging_data.Table_sling_grommet=Table("Data sling/grommet",
                                        default=Table_slings_grommets)
    tab_3.section_1.Rigging_data.Table_sling_grommet.ID_number=TextField("ID number")
    tab_3.section_1.Rigging_data.Table_sling_grommet.Type=OptionField("Type",
                                        options=["sling","grommet"])
    tab_3.section_1.Rigging_data.Table_sling_grommet.SWL = NumberField("SWL")
    tab_3.section_1.Rigging_data.Table_sling_grommet.D = NumberField("D")
    tab_3.section_1.Rigging_data.Table_sling_grommet.n_parts=NumberField("Amount of parts")

    # Table for connections
    tab_3.section_1.Rigging_data.lb9=LineBreak()
    tab_3.section_1.Rigging_data.Table_connecting_points=Table("Connecting points",
                                        default=Table_connect)
    tab_3.section_1.Rigging_data.Table_connecting_points.side=TextField("Which side")
    tab_3.section_1.Rigging_data.Table_connecting_points.connections=AutocompleteField("Connected to "
                                        ,options=drop_list_connect)
    tab_3.section_1.Rigging_data.Table_connecting_points.dia=NumberField("Diameter",suffix='mm')
    tab_3.section_1.Rigging_data.Table_connecting_points.SWL=NumberField("SWL",suffix='t')
