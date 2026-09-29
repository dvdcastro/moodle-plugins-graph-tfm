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
 * The pcbook block links to a pcbook server and shows how many
 * computers are free.
 *
 * The pcbook home page is at http://valis.co.uk/pcbook
 *
 * @package    block_pcbook
 * @copyright  2014 Mike Dawson
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

$plugin->version = 2014101201;
$plugin->requires = 2013111800;
$plugin->cron     = 0;
$plugin->component = 'block_pcbook';
$plugin->release  = 'v1.0';
$plugin->maturity = MATURITY_STABLE;

