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
 * Version metadata for the block_my_certificates plugin.
 *
 * @package   block_my_certificates
 * @copyright Agiledrop, 2026 <[email]>
 * @author    Matej Pal <[email]>
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'block_my_certificates';
$plugin->version   = 2026021100;
$plugin->requires  = 2024100705;
$plugin->dependencies = [
        'mod_customcert' => 2024042212,
];
$plugin->release = '1.2.0';
$plugin->maturity = MATURITY_STABLE;
