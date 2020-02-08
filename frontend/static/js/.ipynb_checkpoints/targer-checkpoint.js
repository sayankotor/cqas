var marks_new = []

var items = Array("Is Python better then PHP for web development?",
    "What is better for deep learning Python or Matlab?",
    "Is Python better than matlab for web development?", "What is better tea or coffee?");


var search_items = Array("single gender schools", "death penalty", "asylum", "chinese medicine");

var item = items[Math.floor(Math.random() * items.length)];

$(function () {

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        $("#displacy").empty()
        $('#displacy-container').hide()
        $('#controls').hide()
    })

    $('#searchArgumentsInput').val(search_items[Math.floor(Math.random() * search_items.length)])
    $('#labelTextt').val(item)

    $('.label_checkbox').bind('click', function () {

         var chkArray = [];
         $(".label_checkbox").each(function () {
             if ($(this).prop('checked')) {
                 chkArray.push($(this).val());
             }
         });
         console.log(chkArray)
         show_entity_labels(chkArray);
     });

    $('#button_label').bind('click', function () {
        label_action()
        return false;
    });
});
const displacy = new displaCyENT('https://api.explosion.ai/displacy/ent/', {
    container: '#displacy'
});

function search_action() {
    $('#displacy-container').show()
    $("#displacy").empty()
    $("#displacy").text("Searching ...")
    var selected_fields = [];
    $(".search_box").each(function () {
        if ($(this).prop('checked')) {
            selected_fields.push($(this).val());
        }
    });

    document.getElementById("button_search").disabled = true;
    console.log(selected_fields)
    $.post("./search_text", {
        username: document.getElementById("searchArgumentsInput").value,
        where: selected_fields,
        confidence: $(".js-range-slider").val()
    })
        .done(function (data) {
            $("#displacy").empty()
            console.log("JSON Data: " + data)
            results = JSON.parse(data)
            var i = 1;
            results.forEach(function (result) {

                var new_marks = []
                new_marks = new_marks.concat(result.query_positions).concat(result.arguments_positions).concat(result.entity_positions)
                var div_element = document.createElement("div")
                div_element.setAttribute("class", "result_div")
                var h = document.createElement("H3")                // Create a <h1> element
                h.setAttribute("class", "nowrap")
                h.innerHTML = "<a class='doc_url' target='_blank' href='" + result.url + "'>" + i + ". " + result.url + "</a>"

                var p = document.createElement("p")                // Create a <h1> element
                div_element.setAttribute("result_id", i)
                var text_full = result.text_full
                var text_full_marked = displacy.search_render(text_full, new_marks)

                var button_analyze = document.createElement("button")
                button_analyze.setAttribute("class", "doc_button_analyze")
                button_analyze.innerHTML = "Analyze"
                button_analyze.setAttribute("full_text", text_full)

                p.setAttribute("class", "description_text")
                p.setAttribute("id", "p_text_" + i)
                if (result.text_full.length > 200) {
                    var short_text = result.text_full.substring(0, 200)
                    while (short_text.slice(-1) != " ") {
                        short_text = short_text.substring(0, short_text.length - 1);
                    }
                    var short_text_marked = displacy.search_render(short_text, new_marks) + " ..."

                    div_element.setAttribute("full_text", text_full_marked)
                    div_element.setAttribute("short_text", short_text_marked);
                    p.innerHTML = text_full_marked;

                    var span = document.createElement("span")
                    var span_text = document.createTextNode("less")
                    span.setAttribute("class", "more_label")
                    span.setAttribute("id", "more_" + i)
                    span.setAttribute("state", "opened")
                    span.appendChild(span_text)
                } else {
                    div_element.setAttribute("full_text", text_full_marked)
                    div_element.setAttribute("short_text", text_full_marked)
                    p.innerHTML = text_full_marked;
                }

                div_element.appendChild(h);
                //div_element.appendChild(button_analyze)
                div_element.appendChild(p);

                if (result.text_full.length > 200) {
                    div_element.appendChild(span)
                }
                $("#displacy").append(div_element);
                i = i + 1
            })

            if (results.length == 0) {
                var h = document.createElement("H1")                // Create a <h1> element
                var t = document.createTextNode("No results found.");     // Create a text node
                h.appendChild(t);
                $("#displacy").append(h);                                   // Append the text to <h1>
            }

            add_listener()
            document.getElementById("button_search").disabled = false;
        })
        .fail(function (jqxhr, textStatus, error) {
            var err = textStatus + ", " + error;
            console.log("Request Failed: " + err);
            var h = document.createElement("H1")                // Create a <h1> element
            var t = document.createTextNode("No results found. (Timeout)");     // Create a text node
            h.appendChild(t);
            $("#displacy").append(h);                                   // Append the text to <h1>
            document.getElementById("button_search").disabled = false;
        });
    return false;
}


function label_action() {
    $("#displacy").empty()
    document.getElementById("button_label").disabled = true
    $("#displacy").text("... Please wait ...");
    $.post("./label_text", {
        username: document.getElementById("labelTextt").value,
        classifier: document.getElementById("model").value
    })
        .done(function (data) {
            $('#Outputt').val(data)
            console.log("JSON Data: " + data)
            marks = JSON.parse(data)
            marks_new = marks

            console.log(marks_new);

            const displacy = new displaCyENT('https://api.explosion.ai/displacy/ent/', {
                container: '#displacy'
            });
            text = document.getElementById("labelTextt").value
            document.getElementById("button_label").disabled = false;
        })
        .fail(function (jqxhr, textStatus, error) {
            $('#Outputt').val("Something went wrong")
            var err = textStatus + ", " + error;
            console.log("Request Failed: " + err);
            document.getElementById("button_label").disabled = false;
        });
}

$("#more_labels").click(function () {
    if ($("#more_labels_box").is(":visible")) {
        $("#more_labels").text("+ more labels");
    } else {
        $("#more_labels").text("- more labels");
    }
    $("#more_labels_box").toggle();
});


function do_label_arg(marks) {
    marks_new = []
    for (var i = 0; i < marks.length; i++) {
        if (i > 0 && i + 1 < marks.length) {
            // Start Label
            if (marks[i].type.substring(0, 1) == "P" && marks[i - 1].type.substring(0, 1) != marks[i].type.substring(0, 1)) {
                var mark = {'type': "PREMISE", 'start': marks[i].start}
                marks_new.push(mark)
            } else if (marks[i].type.substring(0, 1) == "C" && marks[i - 1].type.substring(0, 1) != marks[i].type.substring(0, 1)) {
                var mark = {'type': "CLAIM", 'start': marks[i].start}
                marks_new.push(mark)
            }
            // End Label
            if ((marks[i].type.substring(0, 1) == "P" || marks[i].type.substring(0, 1) == "C")) {
                if (marks[i].type.substring(0, 1) != marks[i + 1].type.substring(0, 1)) {
                    var mark = marks_new.pop()
                    mark.end = marks[i].end
                    marks_new.push(mark)
                }
            }
        } else if (i == 0 && i + 1 < marks.length) {
            // Start Label
            if (marks[i].type.substring(0, 1) == "P") {
                var mark = {'type': "PREMISE", 'start': marks[i].start}
                marks_new.push(mark)
            } else if (marks[i].type.substring(0, 1) == "C") {
                var mark = {'type': "CLAIM", 'start': marks[i].start}
                marks_new.push(mark)
            }
            // End Label
            if ((marks[i].type.substring(0, 1) == "P" || marks[i].type.substring(0, 1) == "C")) {
                if (marks[i].type.substring(0, 1) != marks[i + 1].type.substring(0, 1)) {
                    var mark = marks_new.pop()
                    mark.end = marks[i].end
                    marks_new.push(mark)
                }
            }
        } else if (i == 0 && i + 1 == marks.length) {
            // End Label
            if ((marks[i].type.substring(0, 1) == "P" || marks[i].type.substring(0, 1) == "C")) {
                mark.end = marks[i]
                marks_new.push(mark)
            }
        }
    }
    return marks_new
}


function show_entity_labels(labels) {
    console.log(marks_new);
    const displacy = new displaCyENT('https://api.explosion.ai/displacy/ent/', {
        container: '#displacy'
    });
    text = document.getElementById("labelTextt").value
    ents = labels;
    displacy.render(text, marks_new, ents);
    return false;

}

function add_listener() {
    /*$('.doc_button_analyze').bind('click', function(e) {
        home_page()
        var document_text = e.currentTarget.attributes.full_text.value
        $('#text_to_parse').val(document_text)
        label_action()
    })*/

    $('.more_label').bind('click', function (e) {
        if (e.target.attributes.state.value == "closed") {
            var result_id = e.target.parentNode.attributes.result_id.value
            $('#p_text_' + result_id).html(e.target.parentNode.attributes.full_text.value)
            $('#more_' + result_id).text("less")
            $('#more_' + result_id).attr("state", "opened")
        } else {
            var result_id = e.target.parentNode.attributes.result_id.value
            $('#p_text_' + result_id).html(e.target.parentNode.attributes.short_text.value)
            $('#more_' + result_id).text("more")
            $('#more_' + result_id).attr("state", "closed")
        }
    })
}

function update_slider(my_range) {

    if ($('#premise').is(":checked") || $('#claim').is(":checked")) {
        my_range.update({
            disable: false
        });

    } else {
        my_range.update({
            disable: true
        });
    }
}

$(document).ready(function () {

    $(".js-range-slider").ionRangeSlider();
    var my_range = $(".js-range-slider").data("ionRangeSlider");

    $('#displacy-container').hide()
    $('#controls').hide()

    $('#premise').change(function () {
        update_slider(my_range)
    });

    $('#claim').change(function () {
        update_slider(my_range)
    });

    $('#button_label').bind('click', function () {
        label_action()
    });

    $('#button_search').bind('click', function () {
        search_action()
    });
});

