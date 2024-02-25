// var container = document.getElementById('model-container'); // Corrected container ID
// var scene = new THREE.Scene();
// var camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
// camera.position.z = 5;

// var renderer = new THREE.WebGLRenderer();
// renderer.setSize(container.clientWidth, container.clientHeight);
// container.appendChild(renderer.domElement);

// var jsonData;

// Make an AJAX request to fetch the JSON data
// var xhr = new XMLHttpRequest();
// xhr.open("GET", "{% url 'voxel' %}", true);
// xhr.onload = function () {
//     if (xhr.status === 200) {
//         jsonData = JSON.parse(xhr.responseText);

//         // Create a Three.js volume from the JSON data
//         var width = jsonData.data[0].length;
//         var height = jsonData.data.length;
//         var depth = jsonData.data[0][0].length;
//         var texture = new THREE.DataTexture3D(jsonData.data, width, height, depth);

//         // Create material, geometry, and mesh
//         var material = new THREE.ShaderMaterial({
//             uniforms: {
//                 volume: { value: texture },
//             },
//             vertexShader: document.getElementById('vertexShader').textContent,
//             fragmentShader: document.getElementById('fragmentShader').textContent,
//         });

//         var volumeGeometry = new THREE.BoxGeometry(width, height, depth);
//         var volumeMesh = new THREE.Mesh(volumeGeometry, material);

//         scene.add(volumeMesh);

//         // Animation loop
//         var animate = function () {
//             requestAnimationFrame(animate);
//             volumeMesh.rotation.x += 0.01;
//             volumeMesh.rotation.y += 0.01;
//             renderer.render(scene, camera);
//         };

//         animate();
//     }
// };
// xhr.send();

document.getElementById("resolution").addEventListener("change", e => {
    console.log(e.target.value)
    document.getElementById("res-value").innerHTML = `${e.target.value}`;
})

document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();

    var fileInput = document.getElementById('file-upload');
    var file = fileInput.files[0];

    if (typeof (file) === "undefined" || typeof (file) === null) {
        alert("Please select a file to upload.")
        return
    }

    fetch('/check_access/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({}),
    })
        .then(response => response.json())
        .then(data => {
            if (data.allowed) {
                // User is allowed to perform the action

                var formData = new FormData();
                formData.append('file-upload', file);
                formData.append("resolution", document.getElementById("resolution").value)
                console.log(formData, document.getElementById("resolution").value)

                var xhr = new XMLHttpRequest();
                xhr.open('POST', 'http://127.0.0.1:8000/home/', true);


                xhr.setRequestHeader('X-CSRFToken', window.csrfToken);

                xhr.onload = function () {
                    if (xhr.status === 200) {
                        console.log('Archivo subido correctamente');
                        var response = JSON.parse(xhr.responseText);
                        console.log(response);
                        document.getElementById("threed").setAttribute("url", "embryo.x3d")
                    } else {
                        console.error('Error al subir el archivo:', xhr.responseText);
                    }
                };

                xhr.send(formData);
            } else {
                // User is not allowed
                alert("Access denied, processing limit exceeded. Please wait 24 hours to try again.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});