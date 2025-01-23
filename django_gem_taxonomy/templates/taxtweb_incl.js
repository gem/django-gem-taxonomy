var gem_tax = null;

//
// MAIN
//

function taxtweb_update(prefix, atom_name, prev_value)
{
    var atoms_enabled_name = [];
    var atomsgroups_enabled_name = [];

    if (atom_name != '' && !(atom_name in gem_tax['atom'])) {
        alert('Atom ' + atom_name + 'not recognized.');
        return;
    }

    // this is possible because attributes are independent
    var attribute = gem_tax['attributeinst'][prefix];

    // for each atomsgroup
    for (var atomsgroup_idx in attribute['atomsgroups']) {
        var atomsgroup_key = attribute['atomsgroups'][atomsgroup_idx];
        // search which groups are showed
        var $place_cur = $('#' + prefix + '__' + atomsgroup_key + '_place').children('div');
        if ($place_cur.length == 0) {
            continue;
        }
        atomsgroups_enabled_name.push(atomsgroup_key);

        // for  atomsgroups of ddown type get current selected value
        var $select_cur = $place_cur.find('select#' + prefix + '__' + atomsgroup_key)
        var atom_cur = $select_cur.val();
        if (atom_cur != '') {
            atoms_enabled_name.push(atom_cur);
        }
    }

    atomsgroups_enabled_name.sort(function (a,b) {
        var atomsgroups = gem_tax['atomsgroup'];
        return atomsgroups[a]['prog'] - atomsgroups[b]['prog'];
    });


    // for each enabled atomsgroup check if at least one of the current options
    // is enabled by the current configuration
    // var atomsgroups_cur_enabled_name = atomsgroups_enabled_name.slice();
    for (var atomsgroup_enabled_name_idx in atomsgroups_enabled_name) {
        var atomsgroup_name = atomsgroups_enabled_name[atomsgroup_enabled_name_idx];
        var atomsgroup = gem_tax['atomsgroup'][atomsgroup_name];
        // if the atomsgroup is always visible continue
        if (atomsgroup['is_persistent'])
            continue;

        var atomsgroup_found = false;

        var ref_atom = gem_tax['atomsgroup'][atomsgroup_name]['atoms'][0];
        var atomsgroup_type = gem_tax['atom'][ref_atom]['type']['name'];
        if (atomsgroup_type == 'float' || atomsgroup_type == 'int') {
            console.log('di qui x ' + ref_atom);
            for (var dep_idx in gem_tax['atom'][ref_atom]['deps']) {
                var dep_name = gem_tax['atom'][ref_atom]['deps'][dep_idx];
                if (atoms_enabled_name.includes(dep_name)) {
                    atomsgroup_found = true;
                    break;
                }
            }
            if (!atomsgroup_found) {
                var $place_cur = $('#' + prefix + '__' + atomsgroup_name + '_place');
                $place_cur.empty();
            }
        }
        else if (atomsgroup_type == 'option') {
            // DROPDOWN OPTION
            // get values of the current options
            var $select_cur = $('select#' + prefix + '__' + atomsgroup_name )
            var $options = $select_cur.children('option');
            var option_vals = $.map($options, function(option) { if (option.value != '') return option.value;});

            for (var option_idx in option_vals) {
                var option_val = option_vals[option_idx];

                for (var dep_idx in gem_tax['atom'][option_val]['deps']) {
                    var dep_name = gem_tax['atom'][option_val]['deps'][dep_idx];
                    if (atoms_enabled_name.includes(dep_name)) {
                        atomsgroup_found = true;
                        break;
                    }
                }
                if (atomsgroup_found)
                    break;
            }
            if (!atomsgroup_found) {
                // remove eventually selected option from list before clean it
                var $place_cur = $('#' + prefix + '__' + atomsgroup_name + '_place');
                var $select_cur = $place_cur.find('select#' + prefix + '__' + atomsgroup_name)
                var atom_cur = $select_cur.val();

                if (atom_cur != '') {
                    var idx = atoms_enabled_name.indexOf(atom_cur);
                    if (idx > -1) {
                        // atoms_enabled_name.splice(idx, 1);
                        // atomsgroups_cur_enabled_name.splice(idx, 1);
                        atoms_enabled_name.splice(idx, 1);
                    }
                }
                $place_cur.empty();
            }
        }
    }

    if (atom_name == '') {
        // no new dependencies for 'unknown' value
        return;
    }

    atom = gem_tax['atom'][atom_name];

    var atomsgroups = {};
    for (var rev_dep_id in atom['rev_deps']) {
        var rev_dep = atom['rev_deps'][rev_dep_id];
        var atom_cur = gem_tax['atom'][rev_dep];
        if (!(atom_cur['group'] in atomsgroups)) {
            atomsgroups[atom_cur['group']] = [];
        }
        atomsgroups[atom_cur['group']].push(rev_dep);
    }

    // create new sub-menu
    for (var atomsgroup_key in atomsgroups) {
        var atom_names = atomsgroups[atomsgroup_key];
        $atomsgroup = build_atomsgroup(
            prefix,
            gem_tax['atomsgroup'][atomsgroup_key], atom_names);
        $atomsgroup_place = $('#' + prefix + '__' + atomsgroup_key + '_place');
        $atomsgroup_place.empty();
        $atomsgroup_place.append($atomsgroup);
    }
}

function taxtweb_update_cb(event) {
    var prefix = event.target.id.split('__')[0];
    taxtweb_update(prefix, event.target.value, $(event.target).attr('data_prev'));
    $(event.target).attr('data_prev', event.target.value);
}

function build_atomsddown(prefix, atomsgroup, atoms_list) {
    var $atomsgroup_ddown = $('<select/>').attr('id', prefix + '__' + atomsgroup['name']
                                               ).attr('data_prev', '');
    var add_to_attrib = false;
    for (var atom_id in atoms_list) {
        var atom = gem_tax['atom'][atoms_list[atom_id]];
        if (!add_to_attrib) {
            // if first item add default as unknown as default
            $atom = $('<option/>').attr('value', ''
                                       ).attr('selected', true
                                             ).text('Unknown');
            $atomsgroup_ddown.append($atom);
            add_to_attrib = true;
        }
        $atom = $('<option/>').attr('value', atom['name']
                                   ).text(atom['desc']);
        $atomsgroup_ddown.append($atom);
    }
    if (add_to_attrib) {

        return $atomsgroup_ddown;
    }
    else {
        return null;
    }
}

function build_atomsgroup(prefix, atomsgroup, atom_names) {
    var $atomsgroup = $('<div/>').attr('id', prefix + '__' + atomsgroup['name'] + '_tit').append(
        $('<h5/>').text(atomsgroup['desc']).css('margin-top', '0px'));
    $atomsgroup.css('padding', '8px 8px 8px 16px').css('background-color', '#ffe8e8');

    if (atom_names.length == 1) {
        var atom = gem_tax['atom'][atom_names[0]];
        var atom_type = atom['type'];
        if (atom_type['name'] == 'int' || atom_type['name'] == 'float') {
            $atomsgroup.append($('<p/>').text(atom['desc']));
            $atomsgroup.append($('<input/>').attr('type', 'text'));
            return ($atomsgroup);
        }
    }
    $atomsgroup_ddown = build_atomsddown(prefix, atomsgroup, atom_names);
    if ($atomsgroup_ddown) {
        $atomsgroup_ddown.on('change', taxtweb_update_cb);
        $atomsgroup.append($atomsgroup_ddown);
        return ($atomsgroup);
    }
    else {
        return null;
    }
}

function taxtweb_init() {
    attributes = gem_tax['attribute'];

    for (e in attributes) {
        attribute = gem_tax['attribute'][e];
        var $attribute = $('<div/>').attr('id', attributeinst['name']).append(
            $('<h4/>').text(attributeinst['desc'])).css('background-color', '#fff4f4').css('padding-left', '16px');

        for (a in attribute['atomsgroups']) {
            var atomsgroup = gem_tax['atomsgroup'][attribute['atomsgroups'][a]];

            var $atomsgroup_place = $('<div/>').attr('id', attributeinst['name'] + '__' + atomsgroup['name'] + '_place').css('margin', '8px');
            if (atomsgroup['is_persistent'] == true) {
                var $atomsgroup = build_atomsgroup(attributeinst['name'], atomsgroup, atomsgroup['atoms']);
                if ($atomsgroup != null) {
                    $atomsgroup_place.append($atomsgroup);
                }
            }
            $attribute.append($atomsgroup_place);
        }
        $('#app').append($attribute);
    }
}

function taxtweb_main() {
    console.log(gem_tax);
    taxtweb_init();
}


