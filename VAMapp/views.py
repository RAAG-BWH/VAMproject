from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.http import JsonResponse
import vamtoolbox as vam
import vedo.vtkclasses as vtki
import time
import numpy as np
import vedo
from vedo import dataurl, Plotter, Volume, Text3D
import os

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