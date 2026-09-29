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
 * Plugin local_ibob.
 *
 * @package     local_ibob
 * @category    string
 * @copyright  2023, frederic.grebot <[email]>, L'Institut Agro Dijon, Eduter, CNERTA-WEB
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_ibob';
$plugin->release = '4.0 (2026090100)';
$plugin->version = 2026090100;
$plugin->requires  = 2026052500;         // Requires this Moodle version (5.2).
$plugin->maturity = MATURITY_STABLE;
