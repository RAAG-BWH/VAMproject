function validateFileSize() {
    var input = document.getElementById("file-upload");
    var fileSize = input.files[0].size;
    var maxSize = 1000000 // size in bytes

    if (fileSize > maxSize) {
        alert("File size exceeds the limit. Please choose a smaller file.")
        input.value = ""
    }
}

document.getElementById("resolution").addEventListener("change", e => {
    console.log(e.target.value)
    document.getElementById("res-value").innerHTML = `${e.target.value}`;
})

document.getElementById("uploadForm").addEventListener("submit", function (event) {
    event.preventDefault();

    var fileInput = document.getElementById("file-upload");
    var file = fileInput.files[0];

    if (typeof (file) === "undefined" || typeof (file) === null) {
        alert("Please select a file to upload.")
        return
    }

    // Prevent form submission if CAPTCHA is not completed
    var captchaResponse = grecaptcha.getResponse();
    if (captchaResponse.length == 0) {
        event.preventDefault();
        alert("Please complete the CAPTCHA.");
        return
    }

    fetch("/check_access/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.csrfToken
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
                        console.log('File submitted');
                        var response = JSON.parse(xhr.responseText);
                        console.log(response);
                        document.getElementById("threed").setAttribute("url", "embryo.x3d")
                    } else {
                        console.error('Error when submitting the file:', xhr.responseText);
                    }
                };

                xhr.send(formData);
            } else {
                // User is not allowed
                alert("Access denied, processing limit exceeded. Please wait 48 hours to try again.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});