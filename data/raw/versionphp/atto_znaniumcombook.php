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
 * Book from znanium.com module
 *
 * @package atto_znaniumcombook
 * @copyright 2020 Vadim Dvorovenko
 * @copyright 2020 ООО «ЗНАНИУМ»
 * @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'atto_znaniumcombook';  // Full name of the plugin.
$plugin->version = 2024040300; // The current module version (Date: YYYYMMDDXX).
$plugin->requires = 2016120500; // Requires Moodle 3.2.
$plugin->maturity = MATURITY_STABLE; // Maturity level of this plugin version.
$plugin->release = '2024-04-03'; // Human readable version name.
$plugin->dependencies = [
    'block_znanium_com' => 2024040300,
    'mod_znaniumcombook' => 2024040300,
];
