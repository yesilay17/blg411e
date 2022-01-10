const add_route_button = document.getElementById("add_route_button")
const remove_route_button = document.getElementById("remove_route_button")

add_route_button.addEventListener("click", _ => {
    const route_fields = document.getElementsByClassName("route_field")
    const last_route_field = route_fields[route_fields.length - 1]
    const parent_node = last_route_field.parentNode
    const copy_route_field = last_route_field.cloneNode(deep=true)
    const new_route_field = parent_node.insertBefore(copy_route_field, last_route_field.nextSibling)
    const child_index = Array.prototype.indexOf.call(parent_node.children, new_route_field)
    new_route_field.querySelector("input").name = `route${child_index}`
    new_route_field.querySelector("input").value = ""
    remove_route_button.style.display = "inline"
})

remove_route_button.addEventListener("click", _ => {
    const route_fields = document.getElementsByClassName("route_field")
    const last_route_field = route_fields[route_fields.length - 1]
    const parent_node = last_route_field.parentNode
    parent_node.removeChild(last_route_field)
    
    if (route_fields.length === 1)
    {
        remove_route_button.style.display = "none"
    }
})