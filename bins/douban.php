<?php
    $action = $_REQUEST['action'];
    $doubancli = 'python doubancli.py ';
    try {
        switch ($action) {
            case 'get_captcha':
            case 'is_login':
            case 'skip_song':
            case 'fav_song':
            case 'unfav_song':
            case 'del_song':
            case 'logout':
                exec($doubancli.$action,$out,$states);
                print $out[0];
                break;
            case 'login':
                exec($doubancli.'set_auth '.
                ' '.$_REQUEST['username'].
                ' '.$_REQUEST['password'].
                ' '.$_REQUEST['captcha']);
                exec($doubancli.$action,$out,$states);
                print $out[0];
                break;
            default:
                # code...
                break;
        }
    } catch (Exception $e) {
        echo "{exception:".$e->getMessage()."}";
    }

?>