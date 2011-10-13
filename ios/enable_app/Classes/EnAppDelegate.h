//
//  EnAppDelegate.h
//  enable_app
//
//  Created by John Wiggins on 10/12/11.
//  Copyright Enthought 2011. All rights reserved.
//

#import <UIKit/UIKit.h>

@class EnViewController;

@interface EnAppDelegate : NSObject <UIApplicationDelegate>
{
    UIWindow *window;
    EnViewController *viewController;
}

@property (nonatomic, retain) IBOutlet UIWindow *window;
@property (nonatomic, retain) IBOutlet EnViewController *viewController;

@end

