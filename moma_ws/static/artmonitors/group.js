let selected_color = "#ccccee";
let unselected_color = "#cccccc";

var collections;
var selected_collection_id;
var media_prefix;


function change_collection_checkbox(coll_id) {
    // count number of selected works in collection
    var selected_works = 0;
    var unselected_works = 0;
    var num_works = 0;
    for(var work in collections[coll_id].works){
        num_works++;
        if(collections[coll_id].works[work].selected == "True") {
            selected_works++;
        } else {
            unselected_works++;
        }
    }
    // change checkbox according to selected works
    var coll_checkbox = document.getElementById("cbox-coll-" + coll_id);
    if(selected_works == num_works) {
        coll_checkbox.indeterminate = false;
        coll_checkbox.checked = true;
    } else if (unselected_works == num_works) {
        coll_checkbox.indeterminate = false;
        coll_checkbox.checked = false;
    } else {
        coll_checkbox.indeterminate = true;
    }
}


function select_all_works_for_collection(coll_id) {
    for(var work_id in collections[coll_id].works) {
        collections[coll_id].works[work_id].selected = "True";
        try {
            document.getElementById("cbox-work-" + work_id).checked = true;
            document.getElementById("td-" + work_id).style.backgroundColor = selected_color;
        } catch(e) {}
    }
    change_collection_checkbox(coll_id);
}


function select_no_works_for_collection(coll_id) {
    for(var work_id in collections[coll_id].works){
        collections[coll_id].works[work_id].selected = "False";
        try {
            document.getElementById("cbox-work-" + work_id).checked = false;
            document.getElementById("td-" + work_id).style.backgroundColor = unselected_color;
        } catch(e) {}
    }
    change_collection_checkbox(coll_id);
}


function change_selected_collection_checkbox() {
    change_collection_checkbox(selected_collection_id)
}


function select_all_works() {
    select_all_works_for_collection(selected_collection_id);
}


function select_no_works() {
    select_no_works_for_collection(selected_collection_id);
}


function toggle_selection(work_id) {
    // for the individual work
    var checkbox = document.getElementById("cbox-work-" + work_id);
    var work_td = document.getElementById("td-" + work_id);
    if(checkbox.checked) {
        collections[selected_collection_id].works[work_id].selected = "False";
        checkbox.checked = false;
        work_td.style.backgroundColor = unselected_color;
    } else {
        collections[selected_collection_id].works[work_id].selected = "True";
        checkbox.checked = true;
        work_td.style.backgroundColor = selected_color;
    }
    change_selected_collection_checkbox();
}


function select_all_collections() {
    for(var coll_id in collections) {
        select_all_works_for_collection(coll_id);
    }
}


function select_no_collections() {
    for(var coll_id in collections) {
        select_no_works_for_collection(coll_id);
    }
}


function switch_collection(coll_id) {
    // even if we don't have to switch collections, refresh the state of this one anyway
    if(coll_id == selected_collection_id) {
        for(var work_id in collections[selected_collection_id].works) {
            var checkbox = document.getElementById("cbox-work-" + work_id);
            var work_td = document.getElementById("td-" + work_id);
            if(collections[selected_collection_id].works[work_id].selected == "True") {
                checkbox.checked = true;
                work_td.style.backgroundColor = selected_color;
            } else {
                checkbox.checked = false;
                work_td.style.backgroundColor = unselected_color;
            }
        }
    }
    // deselect current collection
    document.getElementById("li-" + selected_collection_id).style.backgroundColor = unselected_color;
    // switch active collection
    selected_collection_id = coll_id;
    document.getElementById("li-" + selected_collection_id).style.backgroundColor = selected_color;
    document.getElementById("group-coll-abbrev").innerHTML = collections[selected_collection_id].abbrev.toUpperCase();
    document.getElementById("group-coll-name").innerHTML = collections[selected_collection_id].name;
    // prepare inner HTML for the new works table
    var coll_works = collections[selected_collection_id].works;
    var inner_html = "<tr>";
    var counter = 0;
    for(var work_id in coll_works) {
        if(counter == 3) {
            counter = 0;
            inner_html += "</tr><tr>";
        }
        inner_html += "<td id=\"td-";
        inner_html += work_id;
        inner_html += "\" class=\"group-td\" onclick=\"toggle_selection('";
        inner_html += work_id;
        inner_html += "');\"><img id=\"img-";
        inner_html += work_id;
        inner_html += "\" class=\"group-img\" src=\"";
        inner_html += media_prefix + "/" + coll_works[work_id].thumbnail;
        inner_html += "\"><br><p><input type=\"checkbox\" checked=\"checked\" id=\"cbox-work-";
        inner_html += work_id;
        inner_html += "\" click=\";\" onclick=\"toggle_selection('";
        inner_html += work_id;
        inner_html += "')\">";
        inner_html += coll_works[work_id].name;
        inner_html += "</p></td>";
        counter += 1;
    }
    inner_html += "</tr>"
    document.getElementById("innertable").innerHTML = inner_html
    // Now that document has been changed, alter properties as necessary
    for(var work_id in coll_works) {
        var checkbox = document.getElementById("cbox-work-" + work_id);
        var work_td = document.getElementById("td-" + work_id);
        if(coll_works[work_id].selected == "True") {
            checkbox.checked = true;
            work_td.style.backgroundColor = selected_color;
        } else {
            checkbox.checked = false;
            work_td.style.backgroundColor = unselected_color;
        }
    }
}


function update_group_list() {
    // First: there must always be an option for all works
    var inner_html = '<tr><td>All works from all collections</td>' +
                 '<td><input type="button" id="load-all-collections" onclick="select_all_collections();" value="Load"></td>' +
                 '<td><input type="button" value="Delete" disabled></td>' +
                 '<td><a href="/slideshow"><input type="button" value="View slideshow of all works"></a></td></tr>';
    // Second: read from the localstorage for group names only
    // we can retrieve actual data for these later on.
    var local_storage = window.localStorage;
    var local_groups = JSON.parse(local_storage.getItem("saved_groups"));
    for(var entry in local_groups) {
        var group_name = local_groups[entry][0];
        var group_name_uds = group_name.replace(/[\s'"']/g, "_");
        inner_html += '<tr><td>' + group_name + '</td>';
        inner_html += '<td><input type="button" id="load-' + group_name_uds +
                        '" onclick="load_group(\'' + group_name + '\');" value="Load"></td>';
        inner_html += '<td><input type="button" id="delete-' + group_name_uds +
                        '" onclick="delete_group(\'' + group_name + '\');" value="Delete"></td>';
        inner_html += '<td><a href="/slideshow/' + group_name_uds +
                        '"><input type="button" value="View slideshow of this group"></a></td></tr>';
    }
    // assign inner html
    document.getElementById("groupstable").innerHTML = inner_html;
}


function delete_group(group_name) {
    // retrieve groups from local_storage
    var local_storage = window.localStorage;
    var saved_groups = JSON.parse(local_storage.getItem("saved_groups"));
    // remove group from list of groups
    for(var entry in saved_groups) {
        if(saved_groups[entry][0] == group_name) {
            saved_groups.splice(entry, 1);
            break;
        }
    }
    // save change to local_storage
    local_storage.setItem("saved_groups", JSON.stringify(saved_groups))
    update_group_list();
}


function save_current_group() {
    // check for valid name entry
    var group_name = document.getElementById("name-text-field").value;
    if(group_name == "") {
        alert("You must enter a name for this group before you can save it.");
        return;
    }
    // Get a list of all works that are selected
    var selected_works = [];
    for(var coll_id in collections) {
        for(var work_id in collections[coll_id].works) {
            var w = collections[coll_id].works[work_id];
            if(w.selected == "True") {
                selected_works.push([w.name, '/static/media/' + w.path, w.pagename, collections[coll_id].abbrev, work_id, coll_id]);
            }
        }
    }
    // delete existing group with same name
    delete_group(group_name);
    // save this information to local_storage
    var local_storage = window.localStorage;
    try {
        var saved_groups = JSON.parse(local_storage.getItem("saved_groups"));
        saved_groups.push([group_name, selected_works]);
    } catch(e) {
        saved_groups = [];
	saved_groups.push([group_name, selected_works]);
    }
    local_storage.setItem("saved_groups", JSON.stringify(saved_groups));
    // update the group list
    update_group_list();
}


function load_group(group_name) {
    // retrieve group from local_storage
    var local_storage = window.localStorage;
    var saved_groups = JSON.parse(local_storage.getItem("saved_groups"));
    var selected_group_id = -1;
    for(var entry in saved_groups) {
        if(saved_groups[entry][0] == group_name) {
            selected_group_id = entry;
            break;
        }
    }
    if(selected_group_id == -1) {
        alert("Couldn't find that group in your local storage. Please refresh the page and try again.");
        return;
    }
    // load actual group
    var selected_group = saved_groups[selected_group_id][1];
    select_no_collections();
    for(var work_entry in selected_group) {
        var work_data = selected_group[work_entry];
        collections[work_data[5]].works[work_data[4]].selected = "True";
    }
    for(var coll_id in collections) {
        change_collection_checkbox(coll_id);
    }
    // prepare UI
    switch_collection(django_selected_collection);
}


function initialize_grouping(prefix) {
    collections = django_collections;
    selected_collection_id = django_selected_collection;
    media_prefix = prefix

    console.log(collections);

    select_all_collections();
    document.getElementById("li-" + selected_collection_id).style.backgroundColor = selected_color;
    update_group_list();
}
