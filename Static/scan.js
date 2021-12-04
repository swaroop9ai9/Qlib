function ShowCam() {
    Webcam.set({
        width: 450,
        height: 300,
        image_format: 'jpg',
        align: 'center',
        jpeg_quality: 100

    });
    Webcam.attach('#my_camera');
}
window.onload= ShowCam;

function snap() {
    Webcam.snap( function(data_uri) {
        // display results in page
        document.getElementById('results').innerHTML =
        '<img id="image" src="'+data_uri+'"/>';
      } );
}

function upload() {
    console.log("Uploading...")
    var image = document.getElementById('image').src;
    var form = document.getElementById('myForm');
    var formData = new FormData(form);
    formData.append("file", image);
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/capture");
    xmlhttp.onreadystatechange = function() {
    if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        alert(xmlhttp.responseText);
        window.location = "welcome"
        }
    }

    xmlhttp.send(formData);
    console.log(formData.get('file'));
}
