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
 * Version details
 *
 * @package    filter_mapofusers
 * @author     Stefan Weber ([email])
 * @copyright  2025 think-modular
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

// Basics.
$plugin->requires  = 2024100700;
$plugin->component = 'filter_mapofusers';
$plugin->maturity = MATURITY_STABLE;
$plugin->dependencies = [];

// Version.
$plugin->version   = 2026051801;
$plugin->release = '1.0.4 (Build 2026051801)';

// Supported versions.
$plugin->supported = [405, 501];
