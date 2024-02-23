from datetime import datetime, timedelta
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .models import User
import numpy as np
import os
import vamtoolbox as vam
import vedo
import vedo.vtkclasses as vtki
from vedo import dataurl, Plotter, Volume, Text3D

def export_window(fileoutput, binary=False, plt=None):
    try:
        os.remove("embryo.x3d")
    except:
        print("no pasa nada")

    if plt is None:
        plt = vedo.plotter_instance

    fr = fileoutput.lower()
    if fr.endswith(".x3d"):
        #plt.render()
        exporter = vtki.new("X3DExporter")
        exporter.SetBinary(binary)
        exporter.FastestOff()
        exporter.SetInput(plt.window)
        exporter.SetFileName(fileoutput)
        exporter.Update()
        exporter.Write()
        
        wsize = plt.window.GetSize()
    return plt

# /home
def myview(request):
    if request.method == "POST":

        # stl_file = request.FILES['file-upload']
        # mesh = stl.mesh.Mesh.from_file(stl_file)
        # print(f"\n\n\n{request.FILES} hola\n\n\n")
        # print("\n\n\nEmpezando sliceo")
        # print("=====================================")
        # print("=====================================")
        # print("=====================================\n\n\n")
        # 250 is the original resolution
        # 125 is another resolution that goes further
        #target_geo = vam.geometry.TargetGeometry(stlfilename=f"VAMapp/static/{request.FILES['file-upload']}", resolution=15)
        file_path = 'VAMapp/static/{}.stl'.format("a")
                
        with open(file_path, 'wb') as destination:
            for chunk in request.FILES['file-upload'].chunks():
                destination.write(chunk)

        target_geo = vam.geometry.TargetGeometry(stlfilename=file_path, resolution=int(request.POST["resolution"]))
        os.remove(file_path)
        # print("\n\n\nvam.geometry.TargetGeometry done")
        # print("=====================================")
        # print("=====================================")
        # print("=====================================\n\n\n")
        num_angles = 360
        angles = np.linspace(0, 360 - 360 / num_angles, num_angles)
        proj_geo = vam.geometry.ProjectionGeometry(angles,ray_type='parallel',CUDA=True)
        
        # print("\n\n\nvam.geometry.ProjectionGeometry done")
        # print("=====================================")
        # print("=====================================")
        # print("=====================================\n\n\n")
        optimizer_params = vam.optimize.Options(method='PM',n_iter=20,d_h=0.85,d_l=0.6,filter='hamming')
        
        # print("\n\n\nvam.optimize.Options done")
        # print("=====================================")
        # print("=====================================")
        # print("=====================================\n\n\n")
        opt_sino, opt_recon, error = vam.optimize.optimize(target_geo, proj_geo,optimizer_params)
        # print("llego")
        # print("\n\n\n=====================================")
        # print("=====================================")
        # print("=====================================\n\n\n")
        # print("Svam.optimize.optimize done")
        # print("\n\n\nprocedimiento terminado\n\n\n")
        plt = Plotter(size=(400,300), bg='black', axes=3)
        embryo = Volume(target_geo.array).legosurface(vmin=0.5,vmax=1.5)
        plt.render(resetcam=True)
        plt.add(embryo)
        
        export_window('embryo.x3d', binary=False)
        print("Type: \n firefox embryo.html")
        return JsonResponse({"Siiii": "Nooo"})
    else:
        return render(request, "index.html")

def threeD(request):
    return FileResponse(open("embryo.x3d", 'rb'), content_type='model/x3d+xml')

# /voxel
def voxel(request):
    """
    import os
    files_in_static = os.listdir("VAMapp/static")
    print("Files in static directory:")
    for file_name in files_in_static:
        print(file_name)
    """
    print(f"{request} hola\n\n\n")
    print("Empezando sliceo")
    print("=====================================")
    print("=====================================")
    print("=====================================")
    # 250 is the original resolution
    # 125 is another resolution that goes further
    target_geo = vam.geometry.TargetGeometry(stlfilename="VAMapp/static/file.stl", resolution=8)
    print("vam.geometry.TargetGeometry done")
    print("=====================================")
    print("=====================================")
    print("=====================================")
    num_angles = 360
    angles = np.linspace(0, 360 - 360 / num_angles, num_angles)
    proj_geo = vam.geometry.ProjectionGeometry(angles,ray_type='parallel',CUDA=True)
    print("vam.geometry.ProjectionGeometry done")
    print("=====================================")
    print("=====================================")
    print("=====================================")
    optimizer_params = vam.optimize.Options(method='PM',n_iter=20,d_h=0.85,d_l=0.6,filter='hamming')
    print("vam.optimize.Options done")
    print("=====================================")
    print("=====================================")
    print("=====================================")
    opt_sino, opt_recon, error = vam.optimize.optimize(target_geo, proj_geo,optimizer_params)
    print("=====================================")
    print("=====================================")
    print("=====================================")
    print("Svam.optimize.optimize done")
    print(opt_sino, opt_recon, error)
    print("procedimiento terminado")
    
    return HttpResponse({"hola": "hola"})

# /check_access function to determine if the user is allowed to submit a file
def check_access(request):
    allowed = False
    CONNECTIONS_ALLOWED = 2

    user_agent = request.META.get('HTTP_USER_AGENT')
    ip_address = request.META.get('REMOTE_ADDR')
    agent_users = User.objects.filter(user_agent=user_agent)
    ip_users = User.objects.filter(ip_address=ip_address)

    print(user_agent)
    print(ip_address)
    print(type(agent_users))
    print(type(ip_users))
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
        print("======================================")
        print("======================================")
        print("======================================")
        print(">0 ips and 0 agents")
        print("======================================")
        print("======================================")
        print("======================================")
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
        print("======================================")
        print("======================================")
        print("======================================")
        print("0 ips and >0 agents")
        print("======================================")
        print("======================================")
        print("======================================")
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
        print("======================================")
        print("======================================")
        print("======================================")
        print(">0 ips and >0 agents")
        print("======================================")
        print("======================================")
        print("======================================")
    elif len(ip_users) == 0 and len(agent_users) == 0:
        # no register of the user's ip address and the user's user agent (create a new register)
        allowed = True

        # format the datetime object to include only the date, hour, and minute
        # current_datetime = datetime.now()
        # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

        """
        desired_datetime = datetime(
            year=current_datetime.year,
            month=current_datetime.month,
            day=current_datetime.day,
            hour=current_datetime.hour,
            minute=current_datetime.minute
        )
        timezone_aware_datetime = timezone.make_aware(desired_datetime)
        print(timezone_aware_datetime)
        print(type(timezone_aware_datetime))
        """

        date = timezone.now()
        # date = datetime(2015, 10, 9, 23, 55, 59, 342380) 
        print(date)
        print(type(date))

        
        new_obj = User.objects.create(
            user_agent=user_agent,
            ip_address=ip_address,
            n_connections=1,
            last_date_connected=date
        )
        new_obj.save()
        
        
        print("======================================")
        print("======================================")
        print("======================================")
        print("0 ips and 0 agents")
        print("======================================")
        print("======================================")
        print("======================================")

    return JsonResponse({'allowed': allowed})