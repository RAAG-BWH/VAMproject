from django.http import HttpResponse, HttpResponseNotFound, FileResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import User
import numpy as np
import os
import vamtoolbox as vam

import stl

import tempfile

from django.conf import settings

from .forms import CaptchaForm

from PIL import Image, ImageEnhance
import base64
from io import BytesIO
import uuid

from scipy import ndimage

opt_sino = ""

def center_stl(input_filename):
    # stl_mesh = stl.mesh.Mesh.from_file(input_filename)
    stl_mesh = stl.mesh.Mesh(input_filename)

    centroid = np.mean(stl_mesh.points.reshape(-1, 3), axis=0)
    
    stl_mesh.translate(-centroid)
    
    return stl_mesh

# /
def main_view(request):
    if request.method == "GET":
        form = CaptchaForm()
        context = {"form": form}
        return render(request, "index.html", context)
    elif request.method == "POST":
        sino_encoded = False
        id = str(uuid.uuid4())
        print(f"id: {id}")
        file = request.FILES.get("stl")
        resolution = request.POST.get("resolution")   
        contrast = request.POST.get("contrast")  
        resizeFactor = float(request.POST.get("resize"))  

        nameSplit = file.name.split(".")
        
        if (nameSplit[-1].lower() == "stl"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

                stl_mesh = stl.mesh.Mesh.from_file(temp_file_path)
                centroid = np.mean(stl_mesh.points.reshape(-1, 3), axis=0)
                stl_mesh.translate(-centroid)
                stl_mesh.save(temp_file_path)
            
            target_geo = vam.geometry.TargetGeometry(stlfilename=temp_file_path, resolution=resolution)

            num_angles = 360
            angles = np.linspace(0, 360 - 360 / num_angles, num_angles)
            proj_geo = vam.geometry.ProjectionGeometry(angles,ray_type='parallel',CUDA=True)
            
            optimizer_params = vam.optimize.Options(method='OSMO',n_iter=75,d_h=0.85,d_l=0.6,filter='hamming')
            opt_sino, opt_recon, error = vam.optimize.optimize(target_geo, proj_geo,optimizer_params)

            opt_sino.save(f"./{id}")

            with open(f"./{id}.sino", 'rb') as f:
                sino_encoded = base64.b64encode(f.read()).decode('utf-8')

            os.remove(f"./{id}.sino")

            sino = opt_sino.array.transpose(1, 0, 2)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.sino') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            sino = vam.geometry.loadVolume(file_name=temp_file_path).array.transpose(1, 0, 2)

        images = [""] * sino.shape[0]

        for i in range(sino.shape[0]):
            # sinoo = ndimage.rotate(sino[i].T,45)
            # image_array = (sino[i].T * 255).astype(np.uint8)
            image_array = (sino[i].T * 255).astype(np.uint8)
            
            slice = Image.fromarray(image_array)

            enhancer = ImageEnhance.Contrast(slice)

            factor = float(contrast)
            slice = enhancer.enhance(factor)

            # slice = Image.open('1.jpg', 'r')
            slice_w, slice_h = slice.size
            
            new_width = int(slice_w * resizeFactor)

            wpercent = (new_width / float(slice.size[0]))
            hsize = int((float(slice.size[1]) * float(wpercent)))
            slice = slice.resize((new_width, hsize), Image.Resampling.LANCZOS)

            black_img = Image.new(mode="RGB", size=(slice_w, slice_h))

            slice_w, slice_h = slice.size

            black_img_w, black_img_h = black_img.size

            offset = ((black_img_w - slice_w) // 2, (black_img_h - slice_h) // 2)

            black_img.paste(slice, offset)

            buffer = BytesIO()
            black_img.save(buffer, format="PNG")
            buffer.seek(0)

            images[i] = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return JsonResponse({"status": "Success", "images": images, "sino": sino_encoded})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

# /check_access function to determine if the user is allowed to submit a file
def check_access(request):
    if request.method == "POST":
        allowed = False
        CONNECTIONS_ALLOWED = 200000000

        user_agent = request.META.get('HTTP_USER_AGENT')
        ip_address = request.META.get('REMOTE_ADDR')
        agent_users = User.objects.filter(user_agent=user_agent)
        ip_users = User.objects.filter(ip_address=ip_address)

        # print(user_agent)
        # print(ip_address)
        # print(type(agent_users))
        # print(type(ip_users))
        # print(agent_users)
        # print(ip_users)
        # print(len(agent_users) == 0)
        # print(len(ip_users) == 0)

        """
        Some results might have the same ip address but different user agents, for example 2 users
        from the same network but using different devices (users in house, company, etc). So we need
        to check all the ip address if they have the user's ip address, as well as the user agent.
        """
        

        if len(ip_users) > 0 and len(agent_users) == 0:
            # at least one register of the user's ip address and none of the user agent
            max_connections = max([user.n_connections for user in ip_users])
            for user in ip_users:
                if user.n_connections < CONNECTIONS_ALLOWED:
                    user.n_connections += 1
                    user.last_date_connected = timezone.now()
                    user.save()
            if max_connections < CONNECTIONS_ALLOWED: 
                allowed = True
            # print("======================================")
            # print("======================================")
            # print("======================================")
            # print(">0 ips and 0 agents")
            # print("======================================")
            # print("======================================")
            # print("======================================")
        elif len(ip_users) == 0 and len(agent_users) > 0:
            # at least one register of the user's user agent and none of the user's ip address
            max_connections = max([user.n_connections for user in agent_users])
            for user in agent_users:
                if user.n_connections < CONNECTIONS_ALLOWED:
                    user.n_connections += 1
                    user.last_date_connected = timezone.now()
                    user.save()
            if max_connections < CONNECTIONS_ALLOWED: 
                allowed = True
            # print("======================================")
            # print("======================================")
            # print("======================================")
            # print("0 ips and >0 agents")
            # print("======================================")
            # print("======================================")
            # print("======================================")
        elif len(ip_users) > 0 and len(agent_users) > 0:
            # at least one register of the user's ip address and the user's user agent
            unique_agent_users = set(agent_users)
            unique_ip_users = set(ip_users)
            unique_users = unique_agent_users.union(unique_ip_users)
            max_connections = max([user.n_connections for user in unique_users])
            for user in unique_users:
                if user.n_connections < CONNECTIONS_ALLOWED:
                    user.n_connections += 1
                    user.last_date_connected = timezone.now()
                    user.save()
                if max_connections < CONNECTIONS_ALLOWED:
                    allowed = True
            # print("======================================")
            # print("======================================")
            # print("======================================")
            # print(">0 ips and >0 agents")
            # print("======================================")
            # print("======================================")
            # print("======================================")
        elif len(ip_users) == 0 and len(agent_users) == 0:
            # no register of the user's ip address and the user's user agent (create a new register)
            allowed = True

            date = timezone.now()
            # print(date)
            # print(type(date))

            
            new_obj = User.objects.create(
                user_agent=user_agent,
                ip_address=ip_address,
                n_connections=1,
                last_date_connected=date
            )
            new_obj.save()
            
            
            # print("======================================")
            # print("======================================")
            # print("======================================")
            # print("0 ips and 0 agents")
            # print("======================================")
            # print("======================================")
            # print("======================================")

        return JsonResponse({'allowed': allowed})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
# def get_sino(request):
#     # Se accede al archivo .sino guardado "permanentemente" antes. Se elimina ese archivo.
#     response = HttpResponse(open("./hola.sino.sino", "rb"))
#     response['Content-Disposition'] = f'attachment; filename="algo.sino"'
#     os.remove("./hola.sino.sino")
#     return response