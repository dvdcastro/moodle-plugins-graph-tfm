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
 * Defines the metadata for the Quick Course List block
 *
 * @package     block_quickcourselist
 * @author      Mark Johnson <[email]> v2.0
 * @author      Onno Schuit v2.1 commissioned by LTNC B.V.
 * @author      Luuk Verhoeven v3.8 to 4.2.0 commissioned by LTNC B.V.
 * @author      Gemma Lesterhuis v3.10.2 commissioned by LTNC B.V.
 * @copyright   2010 Tauntons College, UK v2.0 and LTNC B.V. v2.1 and further
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later till v2.1, for other versions Freeware
 *              https://ltnc.nl/ltc-plugin-freeware-licentie
 */

defined('MOODLE_INTERNAL') || die;

$plugin->version = 2025060300;
$plugin->requires = 2014051200;
$plugin->component = 'block_quickcourselist';
$plugin->maturity = MATURITY_STABLE;
$plugin->release = '4.5.1';
$plugin->supported = [401, 405];
