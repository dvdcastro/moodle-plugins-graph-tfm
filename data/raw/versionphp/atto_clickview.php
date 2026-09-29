<?php
// This file is part of Moodle - https://moodle.org/
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
// along with Moodle.  If not, see <https://www.gnu.org/licenses/>.

/**
 * Plugin version and other meta-data are defined here.
 *
 * @package     atto_clickview
 * @copyright   2021 ClickView Pty. Limited <[email]>
 * @license     https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version = 2021083004;
$plugin->requires = 2018051700;
$plugin->component = 'atto_clickview';
$plugin->supported = [35, 405];
$plugin->release = 'v3.5-r4 - v4.5-r2';
$plugin->maturity = MATURITY_STABLE;
$plugin->dependencies = [
        'local_clickview' => 2021083005,
];
