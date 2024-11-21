from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    send_from_directory,
    abort
)
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    current_user
)

from app.classes.controllers.admin import Admin_Controllers
from app.classes.controllers.login import User_Login_Controller
from app.classes.controllers.auction_items import Auction_Items_Controller

from app.classes.helpers.auction_item_helpers import Auction_Items_Helpers
from app.classes.helpers.config_helpers import Config_Helpers
from app.classes.helpers.event_helpers import Event_Helpers

app = Flask('__main__', template_folder='app/classes/frontend/templates')

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = "app/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id: str):
    return User_Login_Controller.get_user(user_id)

@app.route('/', methods=['GET'])
def entrypoint():
    return redirect("/login")

@login_manager.unauthorized_handler
def unauthed_request():
    match request.path:
        case '/login':
            return redirect('/login')
        case '/admin/login':
            return redirect('/admin/login')
        
        case _:
            return redirect('/login')

@app.route('/static/assets/<path:path>', methods=['GET'])
def get_static_asset(path):
    return send_from_directory('app/classes/frontend/templates/assets', path)

###################################
#           User Views            #
###################################
@app.route('/login', methods=['GET','POST'])
def user_login():
    match request.method:
        case 'GET':
            org_name = Config_Helpers.get_entity_name()
            return render_template('SignIn.html', org_name=org_name)
        case 'POST':
            email = request.form['email']
            password = request.form['password']
            event_code = request.form['auction_code']
            user = User_Login_Controller.login_user(email, password, event_code)
            if user is not None:
                login_user(user)
                return redirect(f"/events/{Event_Helpers.get_event_id(event_code)}/items")
            else:
                return redirect("/login")
            
@app.route('/events/<int:event_id>/items', methods=['GET'])
@login_required
def auction_items(event_id):
    items = Auction_Items_Controller.get_items(event_id)
    return render_template('Auctions.html', items=items, event_id=event_id)

@app.route('/events/<int:event_id>/items/<int:item_id>', methods=['GET','POST'])
@login_required
def item_details(event_id, item_id):
    match request.method:
        case 'GET':
            item = Auction_Items_Controller.get_item_details(item_id)
            if item["event_id"] == event_id:
                return render_template("AuctionItemInformation.html", item=item, event_id=event_id)
            else:
                return redirect(f"/events/{event_id}/items")
        case 'POST':
            return

###################################
#           Admin Views           #
###################################
@app.route('/admin', methods=['GET'])
def admin_entrypoint():
    return redirect("/admin/login")

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    match request.method:
        case 'GET':
            org_name = Config_Helpers.get_entity_name()
            return render_template("Admin-SignIn.html", org_name=org_name)
        case 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User_Login_Controller.login_admin(email, password)
            if user is not None:
                login_user(user)
                return redirect("/admin/events")
            else:
                return redirect("/admin/login")

@app.route('/admin/events', methods=['GET','POST','PUT','DELETE'])
@login_required
def admin_events():
    if User_Login_Controller.is_admin(current_user.user_id):
        match request.method:
            case 'GET':
                events = Admin_Controllers.EventAdmin_Controller.list_events()
                return render_template("Admin-Auctions.html", events=events)
            case 'POST':
                if request.form['StartTime'] < request.form['EndTime']:
                    Admin_Controllers.EventAdmin_Controller.create_event(
                        event_name = request.form['EventName'],
                        start_time = request.form['StartTime'],
                        end_time = request.form['EndTime']
                    )
                return redirect("/admin/events")
            case 'PUT':
                data = request.get_json()
                Admin_Controllers.EventAdmin_Controller.update_event(
                    event_id = data["event_id"],
                    event_name = data["event_name"],
                    start_time = data["start_time"],
                    end_time = data["end_time"]
                )
                return redirect("/admin/events")
            case 'DELETE':
                Admin_Controllers.EventAdmin_Controller.delete_event(
                    request.get_json()["event_id"]
                )
                return redirect("/admin/events")
    else:
        abort(403)

@app.route('/admin/events/<int:event_id>/items', methods=['GET','DELETE'])
@login_required
def admin_auction_items(event_id):
    if User_Login_Controller.is_admin(current_user.user_id):
        match request.method:
            case 'GET':
                items = Admin_Controllers.EventAdmin_Controller.list_auction_items(event_id)
                return render_template("Admin-Auctions-Items.html", event_id=event_id, items=items)
            case 'DELETE':
                Admin_Controllers.EventAdmin_Controller.delete_auction_item(
                    request.get_json()["item_id"]
                )
                return redirect(f"/admin/events/{event_id}/items")
    else:
        abort(403)

@app.route('/admin/events/<int:event_id>/items/new', methods=['GET','POST'])
@login_required
def admin_new_auction_item(event_id):
    if User_Login_Controller.is_admin(current_user.user_id):
        match request.method:
            case 'GET':
                item = {
                    "item_title": "Item Title",
                    "donor_id": None,
                    "item_description": "Item Description",
                    "item_value": "Item Value"
                }
                donors = Admin_Controllers.DonorAdmin_Controller.list_donors()
                donor_list = []
                for donor in donors:
                    donor_out = {
                        "donor_id": donor["donor_id"],
                        "donor_name": Auction_Items_Helpers.get_donor_name(donor["donor_id"])
                    }
                    donor_list.append(donor_out)
                return render_template("Admin-Auctions-Items-Modify.html", event_id=event_id, item=item, donors=donor_list)
            case 'POST':
                file = request.files['file']
                item_image = "/static/assets/img/placeholder1.png"
                if not file.filename == "":
                    if allowed_file(file.filename):
                        print("reached file upload")
                Admin_Controllers.EventAdmin_Controller.create_auction_item(
                    item_title=request.form["item_title"],
                    item_description=request.form["item_description"],
                    item_price=float(request.form["item_price"]),
                    item_image=item_image,
                    donor_id=int(request.form["donor_id"]),
                    event_id=event_id
                )
                return redirect(f"/admin/events/{event_id}/items")
    else:
        abort(403)

@app.route('/admin/events/<int:event_id>/items/<int:item_id>', methods=['GET','POST'])
@login_required
def admin_edit_auction_item(event_id, item_id):
    if User_Login_Controller.is_admin(current_user.user_id):
        match request.method:
            case 'GET':
                item = Admin_Controllers.EventAdmin_Controller.get_auction_item(item_id)
                donors = Admin_Controllers.DonorAdmin_Controller.list_donors()
                donor_list = []
                for donor in donors:
                    donor_out = {
                        "donor_id": donor["donor_id"],
                        "donor_name": Auction_Items_Helpers.get_donor_name(donor["donor_id"])
                    }
                    donor_list.append(donor_out)
                return render_template("Admin-Auctions-Items-Modify.html", event_id=event_id, item=item, donors=donor_list)
            case 'POST':
                file = request.files['file']
                item_image = Admin_Controllers.EventAdmin_Controller.get_auction_item(item_id).item_image
                if not file.filename == "":
                    if allowed_file(file.filename):
                        print("reached file upload")
                Admin_Controllers.EventAdmin_Controller.update_auction_item(
                    item_id=item_id,
                    item_title=request.form["item_title"],
                    item_description=request.form["item_description"],
                    item_price=float(request.form["item_price"]),
                    item_image=item_image,
                    donor_id=int(request.form["donor_id"]),
                    event_id=event_id,
                    is_active=True
                )
                return redirect(f"/admin/events/{event_id}/items")
    else:
        abort(403)

###################################
#        Auth Placeholders        #
###################################
@app.route('/auth-placeholder', methods=['GET'])
@login_required
def test_page():
    return "Auth worked"

@app.route('/admin/auth-placeholder', methods=['GET'])
@login_required
def test_admin_page():
    if User_Login_Controller.is_admin(current_user.user_id):
        return "Admin auth worked"
    else:
        return redirect("/login")