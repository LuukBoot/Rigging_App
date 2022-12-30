from viktor import ViktorController
from viktor.views import  PlotlyView, PlotlyResult, DataGroup, \
    DataItem, DataResult, DataView,PlotlyAndDataView,SVGView, \
        SVGAndDataView,SVGAndDataResult,SVGResult,Label,GeometryAndDataView,\
            GeometryAndDataResult,PlotlyAndDataResult

from .model import communicater_calculations
from .parametrization import Parametrization
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class Main_Controller(ViktorController):
    label = 'Riggin Checks'
    parametrization = Parametrization

    @PlotlyView("OUTPUT",duration_guess=1)
    def data(self,params,**kwargs):

        data = communicater_calculations(params)
        # gettin data
        max_cog_shift = data.get_max_cog_shift
        load_dis_perc = data.get_load_dis_perc
        load_dis_t = data.get_load_dis_t
        factors = data.get_factors
        N_lifts = data.get_n_lifts
        data_factors = data.get_data_factors
        point_names = ["A","B","C","D"]
        # making figure 
        fig = make_subplots(
            rows=3, cols=1,
            vertical_spacing=0.03,
            specs=[[{"type": "table"}],
                    [{"type": "table"}],
                    [{"type": "table"}]]
            )
        df_table_1= [point_names[:N_lifts],
                     load_dis_perc,
                     load_dis_t,
                     max_cog_shift]

        df_table_2 = [[],[],[]]
        n_ssf_factors = sum('SSF' in s for s in list(factors.keys())) 
        print(n_ssf_factors)
        for key, values in data_factors.items():
            if key!="COG_envelope" and key!="TEF":
                df_table_2[0].append(key)
                df_table_2[1].append(values)
                df_table_2[2].append(factors[key])
        for i in range(n_ssf_factors):
            i +=1
            df_table_2[0].append("SSF"+str(i))
            df_table_2[1].append("Sling safety factor")
            df_table_2[2].append(factors["SSF"+str(i)])
        
        df_table_3= [point_names[:N_lifts],
                     factors["COG_envelope"],
                     factors["TEF"]]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["Point","Load dis[%]","Load dis[t]","Max cog shift[-]"],
                    font=dict(size=15),
                    align="left"
                ),
                cells=dict(
                    values=df_table_1,
                    align = "left",
                    ),
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["What","Answer","Factor[-]"],
                    font=dict(size=15),
                    align="left"
                ),
                cells=dict(
                    values=df_table_2,
                    align = "left",
                    ),
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["point","COG shift factor rigging","TEF factor"],
                    font=dict(size=15),
                    align="left"
                ),
                cells=dict(
                    values=df_table_3,
                    align = "left")
            ),
            row=3, col=1
        )
        
        return PlotlyResult(fig.to_json())        