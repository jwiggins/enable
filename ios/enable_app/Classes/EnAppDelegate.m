//
//  EnAppDelegate.m
//  enable_app
//
//  Created by John Wiggins on 10/12/11.
//  Copyright Enthought 2011. All rights reserved.
//

#import "EnAppDelegate.h"
#import "EnViewController.h"

@implementation EnAppDelegate

@synthesize window;
@synthesize viewController;


- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{    
    // Override point for customization after app launch    
    [window addSubview:viewController.view];
    [window makeKeyAndVisible];

	return YES;
}


- (void)dealloc
{
    [viewController release];
    [window release];
    [super dealloc];
}


@end
