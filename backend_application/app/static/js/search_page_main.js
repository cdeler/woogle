$(function () {
    var titles = ["a"];
    $("#search").autocomplete({
        source: titles
     });
});
function send_user_query(search_mode) {
    $.ajax({
        type: "GET",
        url: "search/",
        dataType: "json",
        data: {
            "user_query": document.getElementById("search").value,
            "search_mode": search_mode
        },
        success: function (response) {
            if (search_mode === 'normal') {
                create_list_view(response, true);
            } else {
                if (search_mode === "short") {
                    titles = Array.from(response);
                } else {
                    create_list_view(response, false);
                }
            }
        }
    });
}

function create_list_view(json, is_button) {
    var list_view = document.getElementById("id_form_list_view");
    list_view.innerHTML = "";
    for(var i = 0; i < json.length; i++) {
        let div = document.createElement("div");
        div.setAttribute("class", "cl_one_cell");

        let a_title = document.createElement("a");
        a_title.setAttribute("id", "id_a_title");
        a_title.innerText = json[i]["title"];
        a_title.setAttribute("href", json[i]["url"]);
        a_title.setAttribute("target", "_blank");

        let a_url = document.createElement("a");
        a_url.setAttribute("id", "id_a_url");
        a_url.innerText = json[i]["url"];
        a_url.setAttribute("href", json[i]["url"]);

        let p_content = document.createElement("p");
        p_content.setAttribute("id", "id_p_content");
        p_content.innerText = json[i]["content"];


        var button = document.createElement("input");
        button.setAttribute("type", "button");
        button.setAttribute("id", json[i]["pageid"]);
        button.setAttribute("class", "cl_button");

        if (is_button === true) {
            st = "send_user_query(" + json[i]["pageid"] +")";
            button.setAttribute("onclick", st);
            button.setAttribute("value", "open full page");
        } else {
            st = "send_user_query('normal')";
            button.setAttribute("onclick", st);
            button.setAttribute("value", "go back");
        }

        div.appendChild(a_title);
        div.appendChild(button);
        div.appendChild(document.createElement("br"));
        div.appendChild(a_url);
        div.appendChild(p_content);
        div.appendChild(document.createElement("hr"));

        list_view.appendChild(div);

     }
}