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
 * Version details for Google Search block.
 *
 * @package    block_google_search
 * @copyright  2026 Antigravity
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2026080301;        // The current plugin version (Date: YYYYMMDDXX).
$plugin->requires  = 2024100100;        // Requires this Moodle version (Moodle 4.5+).
$plugin->supported = [405, 502];        // Supported Moodle branch(es): 4.5.x to 5.2.x.
$plugin->component = 'block_google_search'; // Full name of the plugin.
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = 'v1.1';
