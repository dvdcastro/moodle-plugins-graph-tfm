<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Theme version info
 *
 * @package    theme
 * @subpackage aardvark_postitnote
 * @copyright  2016 Mary Evans {@link: http://vle.bylazydaisy.co.uk
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die;

$plugin->version   = 2016121200; // The current module version (Date: YYYYMMDDXX)
$plugin->requires  = 2016120500; // Requires this Moodle version
$plugin->component = 'theme_aardvark_postitnote'; // Full name of the plugin (used for diagnostics)
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = 'Postit Note (Build: 2016121200)';
$plugin->dependencies = array(
    'theme_base'  => 2016051900,
    'theme_canvas' => 2016052300,
);
