vector  point_normal( int input; int ptnum; ){
    vector nn = 0;
    int prims[] = pointprims( input, ptnum );
    for( int i = 0; i < len( prims ); i++ )
        nn += prim_normal( 0, prims[i], 0.5, 0.5 );
        
    return normalize( nn / len( prims ) );

}