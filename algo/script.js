import * as THREE from 'three'

var container = document.getElementById('model-container'); // Corrected container ID
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
camera.position.z = 5;

var renderer = new THREE.WebGLRenderer();
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

var jsonData;

// Make an AJAX request to fetch the JSON data
var xhr = new XMLHttpRequest();
xhr.open("GET", "{% url 'voxel' %}", true);
xhr.onload = function () {
    if (xhr.status === 200) {
        jsonData = JSON.parse(xhr.responseText);

        // Create a Three.js volume from the JSON data
        var width = jsonData.data[0].length;
        var height = jsonData.data.length;
        var depth = jsonData.data[0][0].length;
        var texture = new THREE.DataTexture3D(jsonData.data, width, height, depth);

        // Create material, geometry, and mesh
        var material = new THREE.ShaderMaterial({
            uniforms: {
                volume: { value: texture },
            },
            vertexShader: document.getElementById('vertexShader').textContent,
            fragmentShader: document.getElementById('fragmentShader').textContent,
        });

        var volumeGeometry = new THREE.BoxGeometry(width, height, depth);
        var volumeMesh = new THREE.Mesh(volumeGeometry, material);

        scene.add(volumeMesh);

        // Animation loop
        var animate = function () {
            requestAnimationFrame(animate);
            volumeMesh.rotation.x += 0.01;
            volumeMesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        };

        animate();
    }
};
xhr.send();


