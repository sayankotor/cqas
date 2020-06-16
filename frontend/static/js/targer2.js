var items = Array("Is Python better then PHP for web development?",
    "What is better for deep learning Python or Matlab?",
    "Is Python better than matlab for web development?", "What is better tea or coffee?");

var search_items = Array("single gender schools", "death penalty", "asylum", "chinese medicine");

var item = items[Math.floor(Math.random() * items.length)];


$('#labelTextt').val(item)
document.getElementById("button_label1").disabled = false;
document.getElementById("button_label1").addEventListener('click',function ()
    {
    document.getElementById("Outputt").innerHTML = "... Please wait ...";
    document.getElementById("button_label1").innerHTML = "Processing";
    document.getElementById("button_label1").disabled = true;
    $("#button_label1").prop('disabled', true);
    $.post("./label_text", {
        username: document.getElementById("labelTextt").value,
        classifier: document.getElementById("model").value,
    })
        .done(function (data) {
            document.getElementById("button_label1").disabled = false;
            document.getElementById("button_label1").innerHTML = "Answer1";
            $('#Outputt').val(data)
            console.log("JSON Data: " + data)
            marks = JSON.parse(data)
            marks_new = marks

            console.log(marks_new);
            const displacy = new displaCyENT('https://api.explosion.ai/displacy/ent/', {
                container: '#displacy'
            });
        })
        .fail(function (jqxhr, textStatus, error) {
            $('#Outputt').val("Something went wrong")
            var err = textStatus + ", " + error;
            console.log("Request Failed: " + err);
            document.getElementById("button_label1").disabled = false;
            document.getElementById("button_label1").innerHTML = "Answer0";
        });
    }  ); 

