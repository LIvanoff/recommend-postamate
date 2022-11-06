import os

from flask import Flask, render_template, request, send_from_directory, current_app
from future.moves import sys
from update_map import folium_update
from recommend import recommend
from XLSXtoPDF import xlsx_to_pdf
from flask_restful import Api, Resource, reqparse


app = Flask(__name__)
app.config['UPLOAD_FOLDER']='docs'


@app.route('/postmethod', methods=['POST'])
def get_post_javascript_data():
    print(request.form, file=sys.stderr)
    
    amount_s  = request.form['amount_s' ]
    kiosk_r   = request.form['kiosk_r'  ]
    mfc_r     = request.form['mfc_r'    ]
    postmat_r = request.form['postmat_r']
    sport_r   = request.form['sport_r'  ]
    apart1_r  = request.form['apart1_r' ]
    apart2_r  = request.form['apart2_r' ]
    apart3_r  = request.form['apart3_r' ]
    apart4_r  = request.form['apart4_r' ]
    apart5_r  = request.form['apart5_r' ]
    geojson   = request.form['geojson'  ]
    
    relevant_dict = {'Жилой дом 40-80': 2,'Жилой дом 80-160': 3,'Жилой дом 40': 1,'Жилой дом 160-200': 4,'Жилой дом 200': 5,'Постамат': 7,'Киоск': 10,'Спортивный объект': 6,'МФЦ': 8}
    
    if kiosk_r:
        relevant_dict['Киоск'            ] = int(kiosk_r  )
    if mfc_r:
        relevant_dict['МФЦ'              ] = int(mfc_r    )
    if postmat_r:
        relevant_dict['Постамат'         ] = int(postmat_r)
    if sport_r:
        relevant_dict['Спортивный объект'] = int(sport_r  )
    if apart1_r:
        relevant_dict['Жилой дом 200'    ] = int(apart1_r )
    if apart2_r:
        relevant_dict['Жилой дом 160-200'] = int(apart2_r )
    if apart3_r:
        relevant_dict['Жилой дом 80-160' ] = int(apart3_r )
    if apart4_r:
        relevant_dict['Жилой дом 40-80'  ] = int(apart4_r )
    if apart5_r:
        relevant_dict['Жилой дом 40'     ] = int(apart5_r )


    if amount_s:
        polygon, points, dataframe    = recommend(geojsonstr=geojson, clusters=int(amount_s), relevant_dict=relevant_dict)
        path, postamat_count, map_id  = folium_update(polygon, points)
    else:
        polygon, points, dataframe    = recommend(geojsonstr=geojson, relevant_dict=relevant_dict)
        path, postamat_count, map_id  = folium_update(polygon, points)

    dataframe = dataframe.reset_index()

    excel_filename = str(map_id) + ".xlsx"
    dataframe.to_excel("./docs/" + excel_filename)

    with open("./templates/result/result_template.txt", "r", encoding="utf-8") as f:
        result_template_str = f.read()

    pdf_filename = str(map_id) + ".pdf"
    xlsx_to_pdf(df=dataframe, path="./docs/" + pdf_filename)

    result_template_str = result_template_str.replace("replace_1", postamat_count                    )
    result_template_str = result_template_str.replace("replace_2", path                              )
    result_template_str = result_template_str.replace("replace_3", "/downloadpdf?id=" + str(map_id)  )
    result_template_str = result_template_str.replace("replace_4", "/downloadexcel?id=" + str(map_id))

    with open("./templates/result/" + map_id + ".html", "x", encoding="utf-8") as f:
        f.write(result_template_str)

    return str(map_id)


@app.route('/')
def index():
    return render_template('map.html')

@app.route('/result')
def result():
    id = request.args.get('id')

    print('result/'+str(id)+'.html', file=sys.stderr)
    return render_template('result/'+ id + '.html')
 

@app.route('/downloadpdf')
def downloadpdf():
    id = request.args.get('id')

    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads, id + ".pdf")


@app.route('/downloadexcel')
def downloadexcel():
    id = request.args.get('id')
    
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads, id + ".xlsx")

@app.route('/test')
def test():
    return render_template('result/result_template.html')

#=============================================================================================

api = Api()

parser = reqparse.RequestParser()
parser.add_argument("geojsonstr", type=str)
parser.add_argument("relevant_dict", type=dict)
parser.add_argument("clusters")


class GeoApi(Resource):
    def get(self):
        return "Access denied", 200

    def post(self):
        data = parser.parse_args()
        print(data, file=sys.stderr)
        try:
            coordinates, return_list, df_for_excel = recommend(data["geojsonstr"], data["relevant_dict"], data["clusters"])
            return [coordinates, return_list], 200
        except Exception as e:
            print(e, file=sys.stderr)
            return "Неверный формат данных!", 500

    def put(self):
        return "Access denied", 200

    def delete(self):
        return "Access denied", 200


api.add_resource(GeoApi, "/api/postmats", "/api/postmats/")
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
