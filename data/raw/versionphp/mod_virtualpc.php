<?php
// This file is part of Virtual PC plugin.
//
// Virtual PC  is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Virtual PC is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

/**
 *
 * This code fragment is called by moodle_needs_upgrading() and /admin/index.php
 *
 * @package    mod_virtualpc
 * @copyright  2014 Universidad de Málaga - Enseñanza Virtual y Laboratorios Tecnólogicos
 * @author     Antonio Godino (asesoramiento [at] evlt [dot] uma [dot] es)
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2015020604;      // The current plugin version (Date: YYYYMMDDXX) XX = date +"%V"
$plugin->requires  = 2016052300;      // Requires this Moodle version
$plugin->cron      = 0;               // Period for cron to check this plugin (secs)
$plugin->component = 'mod_virtualpc'; // To check on upgrade, that plugin sits in correct place.
$plugin->maturity = MATURITY_STABLE; // Stable release
$plugin->release = '3.1.1';         // Human-friendly version name
