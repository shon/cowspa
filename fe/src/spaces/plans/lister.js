plan_panels = function(opt_data, opt_sb, opt_caller) {
    var output = '';
    output += '\n';
    var planList = opt_data.plans;
    var planListLen = planList.length;
    for (var planIndex = 0; planIndex < planListLen; planIndex++) {
        var planData = planList[planIndex];
        output += '\n    <fieldset>\n        <legend> ' + planData.name + ' </legend>\n            <p> ' + planData.description + ' </p>\n    </fieldset>\n    <br/>\n';
    }
    output += '\n';
    return output;
}