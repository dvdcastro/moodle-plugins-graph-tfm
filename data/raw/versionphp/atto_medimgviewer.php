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

/** MEDICAL IMAGING STUDY VIEWER ATTO EDITOR PLUGIN
 * @package    atto_medimgviewer
 * @copyright  2021-2023 Sampsa Lohi & University of Eastern Finland
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

// Full name of the plugin (used for diagnostics).
$plugin->component = 'atto_medimgviewer';
// The current plugin version (Date: YYYYMMDDXX).
$plugin->version = 2022101003;
// Required Moodle version.
$plugin->requires = 2016051900;
$plugin->maturity = MATURITY_BETA;
$plugin->release = '0.1.0';
$plugin->dependencies = [
    'filter_medimgviewer' => 2023020700,
];
