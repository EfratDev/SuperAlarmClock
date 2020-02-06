function toggle_forms() {
    checked = $("#wakeup_time_from_calendar").is(':checked')    
    $("#by_hand_wakeup_form").toggle(!checked)
    $("#calendar_wakeup_form").toggle(checked)
}

$(document).ready(function() {
    toggle_forms()
    $("#wakeup_time_from_calendar").click(toggle_forms)
})