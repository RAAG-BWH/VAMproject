window.addEventListener(
    "message",
    (event) => {
        if (event.data == "full") {
            document.getElementById("img-container").click()
        } else {
            document.getElementById("pika").src = event.data
        }
    },
    false,
  );

document.getElementById("img-container").addEventListener("click", (e) => {
    document.getElementById("img-container").requestFullscreen()
})