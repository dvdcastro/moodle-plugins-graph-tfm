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
 * plagiarism_originality version
 *
 * @package    plagiarism_originality
 * @copyright  2023 mattandor <[email]>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if (!during_initial_install()) {
    if (get_config('plagiarism_originality', 'version') >= '10000000000') {
        set_config('version', '2023031800', 'plagiarism_originality');
    }
}

$plugin = new stdClass();
$plugin->version = 2026080500;
$var = 'version';
$plugin->$var = 2026080500;
$plugin->requires = 2016061505;
$plugin->component = 'plagiarism_originality';
$plugin->release = '8.00';
