space_adm_panels = function(opt_data, opt_sb, opt_caller) {
    var output = '';
    output += '\n';
    var spaceList = opt_data.spaces;
    var spaceListLen = spaceList.length;
    for (var spaceIndex = 0; spaceIndex < spaceListLen; spaceIndex++) {
        var spaceData = spaceList[spaceIndex];
        output += '\n    <fieldset>\n        <legend> ' + spaceData.name + ', ' + spaceData.city + ' </legend>\n            <a href="./' + spaceData.id + '/plans/list"> Plans </a> | \n            <a xref="./' + spaceData.id + '/members"> Members </a> |\n            <a href="./' + spaceData.id + '/plans/new"> New Plan </a>\n    </fieldset>\n    <br/>\n';
    }
    output += '\n';
    return output;
}