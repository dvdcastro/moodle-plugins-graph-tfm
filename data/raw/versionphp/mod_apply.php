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
 * Apply version information
 *
 * @package    mod
 * @subpackage apply 
 * @author     Fumi Iseki
 * @license    GPL
 * @attention  modified from mod_feedback that by Andreas Grabs
 */

defined('MOODLE_INTERNAL') || die();

$plugin->requires  = 2012120300;    // Moodle 2.4
$plugin->component = 'mod_apply';   // Full name of the module (used for diagnostics)
$plugin->cron      = 0;
$plugin->maturity  = MATURITY_STABLE;

$plugin->release   = '1.6.0';       // update messages

$plugin->version   = 2025122200;    // v1.6.0  for Moodle 5.1 (a few layout is changed)
//$plugin->version = 2025020401;    // v1.5.2  for Moodle 4.5
//$plugin->version = 2024040170;    // v1.5.0  merge Andrew Hancox's file upload function
//$plugin->version = 2024010500;    // icon
//$plugin->version = 2023112911;    // modified page show, add export function
//$plugin->version = 2020013000;    // fix call message_send
//$plugin->version = 2019081800;    // minor change for 3.7.1
//$plugin->version = 2018101000;    // support table
//$plugin->version = 2018100300;    //
//$plugin->version = 2016062800;    // 

