function send_user_query() {
    $.ajax({
        type: "GET",
        url: "search/",
        dataType: "json",
        data: {"user_query": document.getElementById("search").value},
        success: function (response) {
            create_list_view(response);
        }
    });
}

function create_list_view(json) {
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

        div.appendChild(a_title);
        div.appendChild(document.createElement("br"));
        div.appendChild(a_url);
        div.appendChild(p_content);
        div.appendChild(document.createElement("hr"));
        list_view.appendChild(div);

     }
}
