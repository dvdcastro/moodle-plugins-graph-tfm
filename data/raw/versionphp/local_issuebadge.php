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
 * Version information for IssueBadge plugin
 *
 * @package    local_issuebadge
 * @copyright  2026 IssueBadge
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_issuebadge';
$plugin->version = 2026012500;           // YYYYMMDDXX format.
$plugin->requires = 2022112800;          // Requires Moodle 4.1+.
$plugin->supported = [401, 405];         // Supported Moodle versions 4.1-4.5.
$plugin->maturity = MATURITY_STABLE;
$plugin->release = '2.0.1';
